"""Tests unitaires pour la configuration de synchronisation, le dialogue de source et le SyncScheduler."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from amso.core.database import DatabaseManager, SourceRecord, SourceType
from amso.core.i18n import get_i18n
from amso.core.scheduler import SyncScheduler
from amso.ui.dialogs.source_config_dialog import SourceConfigDialog
from amso.ui.views.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def db(tmp_path: Path) -> DatabaseManager:
    db_file = tmp_path / "test_sync.db"
    return DatabaseManager(str(db_file))


def test_source_config_dialog_add_mode(qapp: QApplication):
    """Vérifie le dialogue en mode Ajout d'une source."""
    get_i18n().set_language("fr")
    dlg = SourceConfigDialog(initial_path="D:/Musique/Rock")

    assert dlg.edit_name.text() == "Rock"
    assert dlg.edit_path.text() == "D:/Musique/Rock"
    assert dlg.combo_sync_mode.currentData() == "startup"

    # Changer vers intervalle : le spinbox d'intervalle doit devenir visible
    idx_interval = dlg.combo_sync_mode.findData("interval")
    assert idx_interval >= 0
    dlg.combo_sync_mode.setCurrentIndex(idx_interval)
    assert dlg.interval_container.isHidden() is False
    dlg.spin_interval.setValue(45)

    data = dlg.get_data()
    assert data["name"] == "Rock"
    assert data["path_or_uri"] == "D:/Musique/Rock"
    assert data["sync_mode"] == "interval"
    assert data["sync_interval_minutes"] == 45


def test_source_config_dialog_edit_mode(qapp: QApplication):
    """Vérifie le dialogue en mode Modification d'une source existante."""
    get_i18n().set_language("fr")
    source = SourceRecord(
        id=42,
        source_type=SourceType.LOCAL,
        name="Bibliothèque Salon",
        path_or_uri="//NAS/Music",
        sync_mode="realtime",
        sync_interval_minutes=30,
    )

    dlg = SourceConfigDialog(source=source)
    assert dlg.edit_name.text() == "Bibliothèque Salon"
    assert dlg.edit_path.text() == "//NAS/Music"
    assert dlg.edit_path.isReadOnly() is True
    assert dlg.combo_sync_mode.currentData() == "realtime"
    assert dlg.interval_container.isHidden() is True
    assert dlg.realtime_container.isHidden() is False
    assert dlg.spin_realtime.value() == 60

    # Modifier la fréquence temps réel à 45 secondes
    dlg.spin_realtime.setValue(45)
    data_rt = dlg.get_data()
    assert data_rt["sync_mode"] == "realtime"
    assert data_rt["sync_interval_seconds"] == 45

    # Modifier le nom et le mode
    dlg.edit_name.setText("Bibliothèque Salon Renommée")
    idx_manual = dlg.combo_sync_mode.findData("manual")
    dlg.combo_sync_mode.setCurrentIndex(idx_manual)
    assert dlg.realtime_container.isHidden() is True
    assert dlg.interval_container.isHidden() is True

    data = dlg.get_data()
    assert data["name"] == "Bibliothèque Salon Renommée"
    assert data["sync_mode"] == "manual"


def test_source_config_dialog_validation(qapp: QApplication):
    """Vérifie que la validation bloque les champs obligatoires vides."""
    dlg = SourceConfigDialog()
    dlg.edit_name.setText("")
    dlg.edit_path.setText("")

    with patch.object(QMessageBox, "warning") as mock_warn:
        dlg._on_accept()
        assert mock_warn.called
        assert dlg.result() != QDialog.DialogCode.Accepted


def test_source_config_dialog_enter_key_validation(qapp: QApplication):
    """Vérifie que la touche Entrée / Return valide et enregistre le formulaire."""
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QKeyEvent

    dlg = SourceConfigDialog(initial_path="D:/Musique/Pop")
    dlg.edit_name.setText("Pop Renommé")

    # Simuler appui sur la touche Return
    key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    dlg.keyPressEvent(key_event)

    assert dlg.result() == QDialog.DialogCode.Accepted
    data = dlg.get_data()
    assert data["name"] == "Pop Renommé"
    assert data["path_or_uri"] == "D:/Musique/Pop"


def test_sync_scheduler_lifecycle_and_triggers(qapp: QApplication, db: DatabaseManager, tmp_path: Path):
    """Vérifie le démarrage, l'ordonnancement FIFO et les déclencheurs du SyncScheduler."""
    f1 = tmp_path / "audio_source_1"
    f1.mkdir()
    f2 = tmp_path / "audio_source_2"
    f2.mkdir()
    f3 = tmp_path / "audio_source_3"
    f3.mkdir()

    src1 = db.add_source(
        SourceType.LOCAL,
        "Source Démarrage",
        str(f1),
        sync_mode="startup",
    )
    src2 = db.add_source(
        SourceType.LOCAL,
        "Source Intervalle",
        str(f2),
        sync_mode="interval",
        sync_interval_minutes=1,
    )
    src3 = db.add_source(
        SourceType.LOCAL,
        "Source Temps Réel",
        str(f3),
        sync_mode="realtime",
    )

    scheduler = SyncScheduler(db)
    requested_scans: list[SourceRecord] = []
    scheduler.request_scan.connect(requested_scans.append)

    # 1. Enregistrement des répertoires surveillés
    scheduler.refresh_watched_directories()
    assert len(scheduler._watched_paths) >= 1

    # 2. File FIFO et émission de requêtes
    scheduler._enqueue_scan(src1.id)
    scheduler._enqueue_scan(src2.id)

    # Premier scan dépilé
    assert len(requested_scans) == 1
    assert requested_scans[0].id == src1.id

    # Notification de fin du premier scan -> dépilage du second
    scheduler.notify_scan_finished(src1.id)
    assert len(requested_scans) == 2
    assert requested_scans[1].id == src2.id
    scheduler.notify_scan_finished(src2.id)

    # 3. Vérification du déclenchement automatique pour les sources 'startup', 'realtime' ou non scannées
    scheduler._is_running = True
    scheduler._trigger_startup_sources()
    # src1 (startup), src2 (non scannée), src3 (realtime) sont enfilés dans l'ordre de la BDD (1, 2, 3)
    assert len(requested_scans) == 3
    assert requested_scans[2].id == src1.id
    scheduler.notify_scan_finished(src1.id)
    assert len(requested_scans) == 4
    assert requested_scans[3].id == src2.id
    scheduler.notify_scan_finished(src2.id)
    assert len(requested_scans) == 5
    assert requested_scans[4].id == src3.id
    scheduler.notify_scan_finished(src3.id)

    # 4. Arrêt propre du scheduler
    scheduler.stop()


def test_main_window_scheduler_request_scan_handling(qapp: QApplication, db: DatabaseManager, tmp_path: Path):
    """Vérifie que MainWindow._on_scheduler_request_scan gère correctement SourceRecord sans crash."""
    f = tmp_path / "nas_share"
    f.mkdir()
    src = db.add_source(SourceType.LOCAL, "NAS Test", str(f), sync_mode="realtime")

    window = MainWindow(db=db)
    # Appel avec un SourceRecord (tel qu'émis par SyncScheduler.request_scan)
    window._on_scheduler_request_scan(src)
    assert window._current_scanning_source_id == src.id
    assert window.scan_worker is not None

    window.close()


def test_settings_page_sources_table_and_actions(qapp: QApplication, db: DatabaseManager, tmp_path: Path):
    """Vérifie l'affichage des sources dans la page des Paramètres (Option 3 UX Part C)."""
    get_i18n().set_language("fr")
    folder1 = tmp_path / "local1"
    folder1.mkdir()

    src = db.add_source(
        SourceType.LOCAL,
        "Dossier Jazz",
        str(folder1),
        sync_mode="interval",
        sync_interval_minutes=15,
    )

    window = MainWindow(db=db)

    # Ouvrir la page des Paramètres > Général
    window.btn_settings_general.click()
    assert window.stacked_widget.currentIndex() == 2

    # Ouvrir la page des Paramètres > Sources (onglet dédié)
    window.btn_settings_sources.click()
    assert window.stacked_widget.currentIndex() == 4

    # Vérifier que le tableau contient bien la source
    assert hasattr(window, "table_settings_sources")
    assert window.table_settings_sources.rowCount() == 1
    assert "Dossier Jazz" in window.table_settings_sources.item(0, 0).text()
    assert str(folder1) in window.table_settings_sources.item(0, 1).text()
    assert "15 min" in window.table_settings_sources.item(0, 2).text()

    # Vérifier la modification programmatique ou via les paramètres
    window._on_table_source_mode_changed(src, "startup")
    assert db.get_source(src.id).sync_mode == "startup"
    assert "Au démarrage" in window.table_settings_sources.item(0, 2).text()

    # Vérifier que l'action 'Propriétés de la source...' est présente dans le menu contextuel (Option 3 UX Part B)
    ctx_menu = window._create_source_context_menu(src)
    action_texts = [a.text() for a in ctx_menu.actions()]
    assert any("Propriétés" in t for t in action_texts)

    # Tester l'édition d'une source via _on_edit_source_properties
    with (
        patch.object(SourceConfigDialog, "exec", return_value=QDialog.DialogCode.Accepted),
        patch.object(
            SourceConfigDialog,
            "get_data",
            return_value={
                "name": "Dossier Jazz Renommé",
                "path_or_uri": str(folder1),
                "sync_mode": "realtime",
                "sync_interval_minutes": 60,
            },
        ),
    ):
        window._on_edit_source_properties(src)

    # Vérifier la mise à jour en BDD et dans le tableau
    updated_src = db.get_source(src.id)
    assert updated_src.name == "Dossier Jazz Renommé"
    assert updated_src.sync_mode == "realtime"
    assert window.table_settings_sources.item(0, 0).text() == "📁  Dossier Jazz Renommé"
    window.close()


def test_scan_ui_decoupling_and_player_responsiveness(qapp: QApplication, db: DatabaseManager, tmp_path: Path):
    """Vérifie que la synchronisation ne bloque pas la vue Lecteur et met à jour les données de façon découplée."""
    from amso.core.database import TrackRecord
    from amso.core.scanner import ScanSummary
    from amso.ui.views.cover_helper import load_cover_async

    window = MainWindow(db=db)
    # L'utilisateur écoute de la musique sur la page Lecteur
    window._on_player_nav_clicked()
    assert window.stacked_widget.currentWidget() == window.page_player

    # Une synchronisation en arrière-plan termine sa phase 1
    summary1 = ScanSummary(source_id=1, source_path="/music", phase=1, added=5, updated=0, unchanged=10)
    window._on_phase1_scan_finished(summary1)

    # Les données sont marquées sales mais la vue active n'est pas bloquée
    assert window._tracks_dirty is True
    assert window._folders_dirty is True
    assert window.stacked_widget.currentWidget() == window.page_player

    # La synchronisation se termine complètement
    summary2 = ScanSummary(source_id=1, source_path="/music", phase=2, added=5, updated=0, unchanged=10)
    window._on_scan_finished(summary2)
    assert window._tracks_dirty is True

    # Le lecteur reste 100% réactif : changement de piste instantané
    track = TrackRecord(source_ref="test.mp3", source_path="test.mp3", title="Chanson Test", artist="Artiste Test")
    window.page_player.update_track_info(track)
    assert window.page_player.lbl_title.text() == "Chanson Test"

    # Vérification du chargement asynchrone non-bloquant de pochette
    pix = load_cover_async(track, size=320, radius=12)
    assert not pix.isNull()

    # L'utilisateur retourne sur la page Morceaux : le rechargement s'exécute à ce moment (lazy update)
    window._on_all_tracks_clicked()
    assert window._tracks_dirty is False
    assert window.stacked_widget.currentIndex() == 0

    window.close()
