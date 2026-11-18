"""Utilitaire de chargement et de rendu des pochettes audio (Cover Art) pour AMSO.

Garantit un affichage instantané et non-bloquant grâce au cache mémoire et au
chargement asynchrone (aucun gel de l'interface lors de la lecture d'un morceau).
"""

from __future__ import annotations

import os
import zlib
from collections.abc import Callable, Sequence
from pathlib import Path

from PySide6.QtCore import QObject, QPointF, QRectF, Qt, QThread, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

from amso.core.database import TrackRecord
from amso.core.metadata import extract_cover_art, find_cover_image_in_folder
from amso.core.network_paths import is_network_path
from amso.ui.styles import COLOR_BORDER, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT_BRIGHT

# Cache mémoire pour les pochettes (file_path, size) -> QPixmap
_COVER_CACHE: dict[tuple[str, int], QPixmap] = {}
# Cache des signatures des données brutes file_path -> adler32
_COVER_HASH_CACHE: dict[str, int] = {}
# Cache de repli par dossier (folder_path, size) -> (adler32, QPixmap)
_FOLDER_COVER_CACHE: dict[tuple[str, int], tuple[int, QPixmap]] = {}
_DEFAULT_COVERS: dict[tuple[int, int], QPixmap] = {}
_MAX_CACHE_SIZE = 150


def _cache_put(key: tuple[str, int], pixmap: QPixmap) -> None:
    if len(_COVER_CACHE) >= _MAX_CACHE_SIZE:
        _COVER_CACHE.clear()
        _COVER_HASH_CACHE.clear()
        _FOLDER_COVER_CACHE.clear()
    _COVER_CACHE[key] = pixmap


def get_track_cover_hash(track: TrackRecord | None) -> int | None:
    """Retourne le hash adler32 en cache de la pochette pour la piste donnée, ou None."""
    target_path = _resolve_track_target(track)
    if not target_path:
        return 0 if track is None else None
    if target_path in _COVER_HASH_CACHE:
        return _COVER_HASH_CACHE[target_path]
    if track and track.folder_path:
        for (folder, _size), (f_hash, _pix) in _FOLDER_COVER_CACHE.items():
            if folder == track.folder_path:
                return f_hash
    return None


def has_cached_cover(track: TrackRecord | None, size: int = 300) -> bool:
    """Indique si une pochette (fichier ou repli dossier) est déjà disponible en cache mémoire."""
    target_path = _resolve_track_target(track)
    if not target_path:
        return False
    if (target_path, size) in _COVER_CACHE:
        return True
    return bool(track and track.folder_path and (track.folder_path, size) in _FOLDER_COVER_CACHE)


def invalidate_cover_cache(track_or_path: TrackRecord | str | None = None) -> None:
    """Invalide le cache mémoire pour une piste spécifique ou l'intégralité du cache."""
    if not track_or_path:
        _COVER_CACHE.clear()
        _COVER_HASH_CACHE.clear()
        _FOLDER_COVER_CACHE.clear()
        return

    targets: list[str] = []
    if isinstance(track_or_path, TrackRecord):
        resolved = _resolve_track_target(track_or_path)
        if resolved:
            targets.append(resolved)
        for p in (track_or_path.source_path, track_or_path.source_ref, track_or_path.folder_path):
            if p and p not in targets:
                targets.append(p)
    elif isinstance(track_or_path, str) and track_or_path:
        targets.append(track_or_path)

    for path in targets:
        _COVER_HASH_CACHE.pop(path, None)
        keys_to_remove = [k for k in _COVER_CACHE if k[0] == path]
        for k in keys_to_remove:
            _COVER_CACHE.pop(k, None)
        folder_keys = [k for k in _FOLDER_COVER_CACHE if k[0] == path]
        for k in folder_keys:
            _FOLDER_COVER_CACHE.pop(k, None)


def get_default_cover_pixmap(size: int = 300, radius: int = 12) -> QPixmap:
    """Génère et met en cache un visuel par défaut élégant (vinyle & note de musique)."""
    cache_key = (size, radius)
    if cache_key in _DEFAULT_COVERS:
        return _DEFAULT_COVERS[cache_key]

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    rect = QRectF(0, 0, size, size)
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)

    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0.0, QColor("#1E2430"))
    grad.setColorAt(1.0, QColor("#13161C"))
    painter.fillPath(path, QBrush(grad))

    # Cercles concentriques type vinyle
    center = QPointF(size / 2.0, size / 2.0)
    for r in (size * 0.42, size * 0.32, size * 0.22):
        painter.setPen(QPen(QColor(255, 255, 255, 12), 1.5))
        painter.drawEllipse(center, r, r)

    # Disque central
    painter.setBrush(QBrush(QColor(COLOR_PRIMARY)))
    painter.setPen(QPen(QColor(COLOR_PRIMARY_HOVER), 1.5))
    painter.drawEllipse(center, size * 0.12, size * 0.12)

    # Petite note de musique au centre (poids normal pour éviter le faux-gras qui rogne le bord droit de l'emoji)
    painter.setPen(QColor(COLOR_TEXT_BRIGHT))
    font = QFont("Segoe UI", max(7, int(size * 0.13)))
    painter.setFont(font)
    painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), "🎵")

    # Bordure extérieure
    painter.setPen(QPen(QColor(COLOR_BORDER), 1))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)
    painter.end()

    _DEFAULT_COVERS[cache_key] = pixmap
    return pixmap


def _render_cover(raw_data: bytes | None, size: int, radius: int) -> QPixmap:
    """Génère un QPixmap avec coins arrondis à partir des données binaires de l'image."""
    if not raw_data:
        return get_default_cover_pixmap(size, radius)

    image = QImage.fromData(raw_data)
    if image.isNull():
        return get_default_cover_pixmap(size, radius)

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    rect = QRectF(0, 0, size, size)
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)

    scaled_img = image.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x_offset = max(0, (scaled_img.width() - size) // 2)
    y_offset = max(0, (scaled_img.height() - size) // 2)
    cropped_img = scaled_img.copy(x_offset, y_offset, size, size)

    painter.save()
    painter.setClipPath(path)
    painter.drawImage(0, 0, cropped_img)
    painter.restore()

    painter.setPen(QPen(QColor(255, 255, 255, 25), 1))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)
    painter.end()

    return pixmap


def _resolve_track_target(track: TrackRecord | None) -> str | None:
    """Résout le meilleur chemin de fichier ou dossier pour localiser la pochette."""
    if not track:
        return None
    for cand in (track.source_path, track.source_ref, track.folder_path):
        # Appelé sur le thread UI à chaque changement de piste : jamais d'E/S sur un partage réseau
        # (injoignable, elle gèlerait la fenêtre). Le worker gère l'absence du fichier.
        if cand and (is_network_path(cand) or os.path.exists(cand)):
            return cand
    return track.source_path or track.source_ref or track.folder_path


def get_cover_pixmap(
    track: TrackRecord | None,
    size: int = 300,
    radius: int = 12,
    force_refresh: bool = False,
) -> QPixmap:
    """Renvoie de façon synchrone un QPixmap de la pochette d'une piste ou le visuel par défaut."""
    if force_refresh and track:
        invalidate_cover_cache(track)

    target_path = _resolve_track_target(track)
    cache_key = (target_path if target_path else "", size)
    if cache_key[0] and cache_key in _COVER_CACHE:
        return _COVER_CACHE[cache_key]

    raw_data: bytes | None = None
    if target_path and not is_network_path(target_path) and os.path.exists(target_path):
        try:
            raw_data = extract_cover_art(target_path)
        except Exception:
            raw_data = None

        if (
            not raw_data
            and track
            and track.folder_path
            and not is_network_path(track.folder_path)
            and os.path.isdir(track.folder_path)
            and track.folder_path != target_path
        ):
            try:
                raw_data = extract_cover_art(track.folder_path)
            except Exception:
                raw_data = None

    pix = _render_cover(raw_data, size, radius)
    if cache_key[0]:
        _cache_put(cache_key, pix)
        if target_path:
            _COVER_HASH_CACHE[target_path] = zlib.adler32(raw_data) if raw_data else 0
    return pix


class CoverWorker(QThread):
    """Worker QThread dédié à l'extraction asynchrone des métadonnées de pochette."""

    # Ne pas nommer ce signal `finished` : il masquerait QThread.finished, seul signal sûr pour deleteLater().
    cover_ready = Signal(str, int, int, object)  # target_path, size, radius, raw_bytes

    def __init__(
        self,
        target_path: str,
        size: int,
        radius: int,
        folder_path: str | None = None,
        recursive_folder: bool = False,
        fallback_track_paths: Sequence[str] = (),
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.target_path = target_path
        self.size = size
        self.radius = radius
        self.folder_path = folder_path
        self.recursive_folder = recursive_folder
        self.fallback_track_paths = tuple(fallback_track_paths)
        self.callbacks: list[Callable[[str, QPixmap], None]] = []

    def run(self) -> None:
        raw_bytes: bytes | None = None
        if self.recursive_folder:
            if os.path.isdir(self.target_path):
                try:
                    raw_bytes = find_cover_image_in_folder(Path(self.target_path), recursive=True)
                except Exception:
                    raw_bytes = None
            if not raw_bytes:
                for track_path in self.fallback_track_paths:
                    if os.path.isfile(track_path):
                        try:
                            raw_bytes = extract_cover_art(track_path)
                        except Exception:
                            raw_bytes = None
                        if raw_bytes:
                            break
        else:
            if os.path.exists(self.target_path):
                try:
                    raw_bytes = extract_cover_art(self.target_path)
                except Exception:
                    raw_bytes = None

            if (
                not raw_bytes
                and self.folder_path
                and os.path.isdir(self.folder_path)
                and self.folder_path != self.target_path
            ):
                try:
                    raw_bytes = extract_cover_art(self.folder_path)
                except Exception:
                    raw_bytes = None

        self.cover_ready.emit(self.target_path, self.size, self.radius, raw_bytes)


_ACTIVE_COVER_WORKERS: list[CoverWorker] = []


def _load_path_cover_async(
    target_path: str | None,
    folder_path: str | None = None,
    size: int = 300,
    radius: int = 12,
    callback: Callable[[str, QPixmap], None] | None = None,
    force_check: bool = True,
    recursive_folder: bool = False,
    fallback_track_paths: Sequence[str] = (),
) -> QPixmap:
    """Partage le cache et le worker asynchrone pour charger une pochette de fichier ou de dossier."""
    if not target_path:
        return get_default_cover_pixmap(size, radius)

    cache_key = (target_path, size)
    cached_pixmap = _COVER_CACHE.get(cache_key)
    folder_cached = _FOLDER_COVER_CACHE.get((folder_path, size)) if cached_pixmap is None and folder_path else None

    # Visuel de retour immédiat pour l'IHM (fichier en cache, sinon repli dossier, sinon défaut)
    if cached_pixmap is not None:
        immediate_pix = cached_pixmap
    elif folder_cached is not None:
        immediate_pix = folder_cached[1]
    else:
        immediate_pix = get_default_cover_pixmap(size, radius)

    # Si déjà en cache et qu'une vérification n'est pas demandée
    if cached_pixmap is not None and not force_check:
        return immediate_pix

    # Éviter d'empiler plusieurs workers identiques actifs, tout en notifiant tous les demandeurs
    for w in _ACTIVE_COVER_WORKERS:
        if w.target_path == target_path and w.size == size and w.recursive_folder == recursive_folder and w.isRunning():
            if callback and callback not in w.callbacks:
                w.callbacks.append(callback)
            return immediate_pix

    worker = CoverWorker(
        target_path,
        size,
        radius,
        folder_path=folder_path,
        recursive_folder=recursive_folder,
        fallback_track_paths=fallback_track_paths,
    )
    if callback:
        worker.callbacks.append(callback)

    def _on_worker_finished(p: str, s: int, r: int, raw_bytes: bytes | None) -> None:
        new_hash = zlib.adler32(raw_bytes) if raw_bytes else 0
        old_hash = _COVER_HASH_CACHE.get(p)

        # Si les données brutes ont changé ou si l'élément n'était pas en cache
        if (p, s) not in _COVER_CACHE or new_hash != old_hash:
            pix = _render_cover(raw_bytes, s, r)
            _cache_put((p, s), pix)
            _COVER_HASH_CACHE[p] = new_hash
            if folder_path and raw_bytes:
                _FOLDER_COVER_CACHE[(folder_path, s)] = (new_hash, pix)
            for cb in list(worker.callbacks):
                try:
                    cb(p, pix)
                except Exception:
                    pass

    def _on_thread_finished() -> None:
        if worker in _ACTIVE_COVER_WORKERS:
            _ACTIVE_COVER_WORKERS.remove(worker)
        worker.deleteLater()

    worker.cover_ready.connect(_on_worker_finished)
    worker.finished.connect(_on_thread_finished)
    _ACTIVE_COVER_WORKERS.append(worker)
    worker.start()
    return immediate_pix


def load_cover_async(
    track: TrackRecord | None,
    size: int = 300,
    radius: int = 12,
    callback: Callable[[str, QPixmap], None] | None = None,
    force_check: bool = True,
) -> QPixmap:
    """Renvoie immédiatement le visuel (en cache ou défaut) et vérifie/charge la pochette en tâche de fond.

    Garantit zéro blocage sur le thread d'interface Qt lors du changement de morceau
    tout en détectant dynamiquement tout changement de fichier d'image de dossier (folder.png/jpg/ico).
    """
    target_path = _resolve_track_target(track)
    folder_path = track.folder_path if track else None
    return _load_path_cover_async(
        target_path,
        folder_path=folder_path,
        size=size,
        radius=radius,
        callback=callback,
        force_check=force_check,
    )


def load_folder_cover_async(
    folder_path: str | None,
    size: int = 300,
    radius: int = 12,
    callback: Callable[[str, QPixmap], None] | None = None,
    force_check: bool = True,
    fallback_track_paths: Sequence[str] = (),
) -> QPixmap:
    """Charge de façon asynchrone l'image de pochette d'un dossier (ex. dossier artiste)."""
    if not folder_path:
        return get_default_cover_pixmap(size, radius)
    # Ne jamais sonder un partage réseau sur le thread UI ; le worker gère son accessibilité.
    if not is_network_path(folder_path) and not os.path.isdir(folder_path):
        return get_default_cover_pixmap(size, radius)
    return _load_path_cover_async(
        folder_path,
        folder_path=folder_path,
        size=size,
        radius=radius,
        callback=callback,
        force_check=force_check,
        recursive_folder=True,
        fallback_track_paths=fallback_track_paths,
    )


def wait_for_cover_workers(timeout_ms: int = 1500) -> int:
    """Attend la fin des extractions de pochette en cours ; retourne le nombre de threads encore actifs.

    À appeler à la fermeture : détruire un QThread en cours d'exécution provoque
    « QThread: Destroyed while thread is still running » et un risque de crash.
    """
    for worker in list(_ACTIVE_COVER_WORKERS):
        worker.wait(timeout_ms)
    return sum(1 for w in _ACTIVE_COVER_WORKERS if w.isRunning())
