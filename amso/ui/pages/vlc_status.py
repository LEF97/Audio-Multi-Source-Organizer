"""Libellé de statut de libvlc (réglages du lecteur), partagé entre la construction de la page et sa retraduction."""

from __future__ import annotations

from amso.core.i18n import tr
from amso.services.player_service import PlayerService
from amso.services.vlc_info import describe_libvlc


def build_vlc_status(player_service: PlayerService | None) -> tuple[str, str]:
    """Retourne (HTML du statut, infobulle avec le chemin de la libvlc chargée)."""
    is_avail = bool(player_service and player_service.is_vlc_available)
    status_txt = tr("settings.player_engine_active") if is_avail else tr("settings.player_engine_inactive")
    status_color = "#34D399" if is_avail else "#EF4444"
    html = (
        f"• <b>{tr('settings.player_engine_status')}</b> "
        f"<span style='color: {status_color}; font-weight: 600;'>{status_txt}</span>"
    )
    info = describe_libvlc() if is_avail else None
    if info is None:
        return html, ""
    origin = tr(f"settings.vlc_origin_{info.origin.value}")
    html += f"<br>• <b>{tr('settings.player_engine_lib')}</b> libVLC {info.version} — {origin}"
    return html, info.path
