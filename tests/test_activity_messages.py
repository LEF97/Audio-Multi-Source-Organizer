"""Journal d'activité : clé + paramètres stockés, traduits à l'affichage ; colonne ajoutée sans perte de données."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from amso.core.activity_messages import (
    LogMessage,
    decode,
    display_action,
    display_details,
    display_level,
    raw_line,
)
from amso.core.database import DatabaseManager
from amso.core.i18n import get_i18n


@pytest.fixture
def db(tmp_path: Path) -> DatabaseManager:
    return DatabaseManager(tmp_path / "logs.db")


def test_add_activity_log_message_stocke_le_rendu_francais_et_le_json(db: DatabaseManager) -> None:
    db.add_activity_log(
        action=LogMessage("log.sync_success", {"source": "Par artiste"}),
        details=[LogMessage("log.detail_added", {"count": 3}), raw_line("erreur système")],
    )

    rec = db.get_activity_logs()[0]

    assert rec.action == "Synchronisation réussie : Par artiste"
    assert rec.details == "Morceaux ajoutés : 3\nerreur système"
    action, lines = decode(rec.i18n)
    assert action == LogMessage("log.sync_success", {"source": "Par artiste"})
    assert [m.key for m in lines] == ["log.detail_added", "log.raw"]


def test_display_action_suit_la_langue_active(db: DatabaseManager, monkeypatch: pytest.MonkeyPatch) -> None:
    db.add_activity_log(action=LogMessage("log.sync_success", {"source": "X"}))
    rec = db.get_activity_logs()[0]
    i18n = get_i18n()
    monkeypatch.setattr(i18n, "_translations", {"log.sync_success": "同期成功: {source}"})

    assert display_action(rec) == "同期成功: X"


def test_display_entree_ancienne_sans_json_garde_le_texte_stocke(db: DatabaseManager) -> None:
    db.add_activity_log(action="Synchronisation réussie : Ancienne", details="Durée : 2.4s")

    rec = db.get_activity_logs()[0]

    assert rec.i18n is None
    assert display_action(rec) == "Synchronisation réussie : Ancienne"
    assert display_details(rec) == "Durée : 2.4s"


def test_decode_json_illisible_retourne_le_repli_sans_exception() -> None:
    assert decode("{pas du json") == (None, [])
    assert decode('{"action": {}}') == (None, [])
    assert decode(None) == (None, [])


def test_display_level_traduit_les_niveaux_connus_et_garde_les_autres() -> None:
    assert display_level("SUCCESS") == get_i18n().tr("logs.filter_success")
    assert display_level("AUTRE") == "AUTRE"


def test_migration_ajoute_la_colonne_i18n_sans_perdre_les_entrees(tmp_path: Path) -> None:
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL DEFAULT 'INFO', category TEXT NOT NULL DEFAULT 'SYNC', source_name TEXT,
            action TEXT NOT NULL, details TEXT, items_added INTEGER DEFAULT 0, items_updated INTEGER DEFAULT 0,
            items_deleted INTEGER DEFAULT 0, items_errors INTEGER DEFAULT 0)"""
    )
    conn.execute("INSERT INTO activity_logs (action) VALUES ('Entrée ancienne')")
    conn.commit()
    conn.close()

    first = DatabaseManager(path)
    second = DatabaseManager(path)  # idempotence : relancer ne doit rien changer

    assert first.get_activity_logs()[0].action == "Entrée ancienne"
    assert second.get_activity_logs()[0].i18n is None
    with sqlite3.connect(path) as check:
        columns = [r[1] for r in check.execute("PRAGMA table_info(activity_logs);")]
    assert columns.count("i18n") == 1
