"""Messages du journal d'activité stockés sous forme de clé + paramètres, traduits à l'affichage.

Le journal est persistant : un texte écrit en français resterait en français dans toutes les langues. La colonne
`i18n` garde la clé et les paramètres ; les colonnes `action` et `details` conservent le rendu français pour la
recherche, l'export et les entrées antérieures à cette colonne.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from amso.core.db.models import ActivityLogRecord

logger = logging.getLogger(__name__)

LEVEL_LABEL_KEYS = {
    "SUCCESS": "logs.filter_success",
    "INFO": "logs.filter_info",
    "WARNING": "logs.filter_warning",
    "ERROR": "logs.filter_error",
}


@dataclass(slots=True, frozen=True)
class LogMessage:
    key: str
    params: dict[str, Any] = field(default_factory=dict)


def raw_line(text: str) -> LogMessage:
    """Texte non traduisible (message d'erreur système, chemin) : affiché tel quel."""
    return LogMessage("log.raw", {"text": text})


def render_source_language(message: LogMessage) -> str:
    # Import différé : amso.core.i18n dépend de la config, donc de la base, qui charge ce module via activity_repo
    from amso.core.i18n import get_i18n

    return get_i18n().tr_source(message.key, **message.params)


def render(message: LogMessage) -> str:
    from amso.core.i18n import tr

    return tr(message.key, **message.params)


def encode(action: LogMessage, details: list[LogMessage] | None) -> str:
    payload: dict[str, Any] = {"action": _to_dict(action)}
    if details:
        payload["details"] = [_to_dict(m) for m in details]
    return json.dumps(payload, ensure_ascii=False)


def _to_dict(message: LogMessage) -> dict[str, Any]:
    return {"key": message.key, "params": message.params}


def _from_dict(data: dict[str, Any]) -> LogMessage:
    return LogMessage(str(data["key"]), dict(data.get("params") or {}))


def decode(payload: str | None) -> tuple[LogMessage | None, list[LogMessage]]:
    """(action, lignes de détail) ; (None, []) pour une entrée sans clé ou un JSON illisible."""
    if not payload:
        return None, []
    try:
        data = json.loads(payload)
        action = _from_dict(data["action"])
        details = [_from_dict(d) for d in data.get("details", [])]
    except (ValueError, KeyError, TypeError) as exc:
        logger.warning("Entrée de journal illisible (%s) : texte français conservé", exc)
        return None, []
    return action, details


def display_action(record: ActivityLogRecord) -> str:
    action, _ = decode(record.i18n)
    return render(action) if action else record.action


def display_details(record: ActivityLogRecord) -> str:
    _, lines = decode(record.i18n)
    return "\n".join(render(m) for m in lines) if lines else (record.details or "")


def display_level(level: str) -> str:
    from amso.core.i18n import tr

    key = LEVEL_LABEL_KEYS.get(level)
    return tr(key) if key else level
