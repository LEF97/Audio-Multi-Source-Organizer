"""Tests unitaires pour le journal d'activité (Logs) et le popover du fil des actions (AMSO)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from amso.core.database import DatabaseManager, SourceType
from amso.core.scheduler import SyncScheduler
from amso.ui.views.activity_feed_popover import ActivityFeedPopover
from amso.ui.views.logs_view import LogsView
from amso.ui.views.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    """Fixture fournissant une instance QApplication pour les tests d'IHM."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def temp_db():
    """Fixture fournissant une base de données temporaire isolée."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_logs.db"
        db = DatabaseManager(db_path=db_path)
        db.init_schema()
        try:
            yield db
        finally:
            db.close()


def test_activity_logs_crud(temp_db: DatabaseManager):
    """Vérifie l'insertion, le filtrage, la recherche et le nettoyage des logs."""
    # 1. Insertion de plusieurs logs
    log1_id = temp_db.add_activity_log(
        action="Scan terminé",
        level="SUCCESS",
        category="SYNC",
        source_name="Musique",
        details="Ajouts: 12, Modifiés: 2",
        items_added=12,
        items_updated=2,
    )
    assert log1_id > 0

    log2_id = temp_db.add_activity_log(
        action="Échec de scan",
        level="ERROR",
        category="SYNC",
        source_name="Téléchargements",
        details="Accès refusé au disque",
        items_errors=1,
    )
    assert log2_id > log1_id

    log3_id = temp_db.add_activity_log(
        action="Source ajoutée",
        level="INFO",
        category="LIBRARY",
        source_name="NAS",
        details="Mode: realtime",
    )
    assert log3_id > log2_id

    # 2. Récupération globale
    all_logs = temp_db.get_activity_logs(limit=10)
    assert len(all_logs) == 3
    # Tri décroissant par défaut (les plus récents en premier)
    assert all_logs[0].action == "Source ajoutée"
    assert all_logs[1].action == "Échec de scan"
    assert all_logs[2].action == "Scan terminé"

    # 3. Filtrage par niveau
    success_logs = temp_db.get_activity_logs(level="SUCCESS")
    assert len(success_logs) == 1
    assert success_logs[0].items_added == 12

    error_logs = temp_db.get_activity_logs(level="ERROR")
    assert len(error_logs) == 1
    assert error_logs[0].level == "ERROR"

    # 4. Recherche par mot-clé
    search_nas = temp_db.get_activity_logs(search="NAS")
    assert len(search_nas) == 1
    assert search_nas[0].source_name == "NAS"

    search_details = temp_db.get_activity_logs(search="refusé")
    assert len(search_details) == 1
    assert search_details[0].level == "ERROR"

    # 5. Comptage
    count_all = temp_db.count_activity_logs()
    assert count_all == 3
    assert temp_db.count_activity_logs(level="ERROR") == 1
    assert temp_db.count_activity_logs(level="INFO") == 1

    # 6. Vidage des logs
    deleted = temp_db.clear_activity_logs()
    assert deleted == 3
    assert temp_db.count_activity_logs() == 0


def test_scheduler_status(temp_db: DatabaseManager, qapp):
    """Vérifie le calcul d'état du planificateur pour le fil d'actions."""
    scheduler = SyncScheduler(temp_db)
    status = scheduler.get_schedule_status()
    assert status["current_source"] is None
    assert status["queue_sources"] == []
    assert status["upcoming"] == []

    # Ajout d'une source périodique et d'une source en continu
    s1 = temp_db.add_source(
        source_type=SourceType.LOCAL,
        name="Source Périodique",
        path_or_uri="C:/Music1",
        sync_mode="interval",
        sync_interval_minutes=30,
    )
    s2 = temp_db.add_source(
        source_type=SourceType.LOCAL,
        name="Source Temps Réel",
        path_or_uri="C:/Music2",
        sync_mode="realtime",
    )

    # Début de scan simulé
    scheduler.notify_scan_started(s1.id)
    scheduler.enqueue_source(s2.id)

    status_updated = scheduler.get_schedule_status()
    assert status_updated["current_source"] is not None
    assert status_updated["current_source"].name == "Source Périodique"
    assert len(status_updated["queue_sources"]) == 1
    assert status_updated["queue_sources"][0].name == "Source Temps Réel"
    assert len(status_updated["upcoming"]) >= 1

    scheduler.notify_scan_finished(s1.id)


def test_activity_feed_popover(temp_db: DatabaseManager, qapp):
    """Vérifie le rendu et les signaux du popover ActivityFeedPopover."""
    scheduler = SyncScheduler(temp_db)
    popover = ActivityFeedPopover(temp_db, scheduler=scheduler)

    # Ajouter quelques logs récents
    temp_db.add_activity_log(
        action="Synchro terminée",
        level="SUCCESS",
        source_name="Source Test",
        items_added=5,
    )

    popover.refresh_content()
    assert "PRÊT" in popover.lbl_badge_status.text()

    # Simulation d'action en cours
    s = temp_db.add_source(
        source_type=SourceType.LOCAL,
        name="Disque Ext",
        path_or_uri="D:/Ext",
        sync_mode="manual",
    )
    scheduler.notify_scan_started(s.id)
    popover.update_progress("Indexation 10/50 : file.flac", pct=20)
    popover.refresh_content()
    assert "SYNCHRO" in popover.lbl_badge_status.text()
    assert popover.cur_progress.value() == 20

    # Signal open_logs_requested
    received = []
    popover.open_logs_requested.connect(lambda: received.append(True))
    popover._on_open_logs()
    assert len(received) == 1

    scheduler.notify_scan_finished(s.id)


def test_logs_view(temp_db: DatabaseManager, qapp):
    """Vérifie l'affichage, les filtres et l'export dans LogsView."""
    view = LogsView(temp_db)
    view.refresh_logs()
    assert view.table.rowCount() == 0

    # Insérer logs de différents niveaux
    temp_db.add_activity_log("Scan 1", level="SUCCESS", source_name="S1", items_added=4)
    temp_db.add_activity_log("Scan 2", level="ERROR", source_name="S2", details="Erreur I/O")
    temp_db.add_activity_log("Scan 3", level="WARNING", source_name="S3", details="Fichiers ignorés")

    view.refresh_logs()
    assert view.table.rowCount() == 3

    # Filtrage par niveau SUCCESS
    idx = view.combo_level.findData("SUCCESS")
    view.combo_level.setCurrentIndex(idx)
    assert view.table.rowCount() == 1
    assert view.table.item(0, 3).text() == "Scan 1"

    # Filtrage par recherche
    idx_all = view.combo_level.findData("ALL")
    view.combo_level.setCurrentIndex(idx_all)
    view.search_edit.setText("I/O")
    assert view.table.rowCount() == 1
    assert view.table.item(0, 3).text() == "Scan 2"


def test_main_window_logs_integration(temp_db: DatabaseManager, qapp):
    """Vérifie l'intégration du bouton Logs et de la page Logs dans MainWindow."""
    window = MainWindow(db=temp_db)
    window.show()

    # 1. Vérification des éléments d'IHM
    assert hasattr(window, "btn_settings_logs")
    assert hasattr(window, "page_logs")
    assert hasattr(window, "btn_activity_feed")
    assert hasattr(window, "activity_popover")

    # 2. Navigation vers la page Logs
    window.show_logs_page()
    assert window.stacked_widget.currentWidget() == window.page_logs
    assert window.btn_settings_logs.isChecked()

    # 3. Fermeture
    window.close()


def test_player_error_logs_and_clickable_status(temp_db: DatabaseManager, qapp):
    """Vérifie que les alertes du lecteur sont enregistrées dans les logs et que la barre d'état est cliquable."""
    window = MainWindow(db=temp_db)
    window.show()

    # Initialement prêt et curseur normal
    assert "⚠️" not in window.status_label.text()

    # Émission d'une erreur de fichier introuvable
    err_text = "Fichier audio introuvable : D:/Music/dummy.mp3"
    window.player_service.error_occurred.emit(err_text)

    # 1. Barre d'état mise à jour avec avertissement et curseur interactif
    assert err_text in window.status_label.text()
    assert window.status_label.cursor().shape() == Qt.CursorShape.PointingHandCursor

    # 2. Enregistrement dans la base de données
    logs = temp_db.get_activity_logs(limit=10)
    assert len(logs) == 1
    assert logs[0].category == "PLAYER"
    assert logs[0].level == "WARNING"
    assert err_text in logs[0].details
    assert logs[0].items_errors == 1

    # 3. Rafraîchissement automatique de la vue Logs
    assert window.page_logs.table.rowCount() == 1

    # 4. Clic sur la barre d'état ouvre directement la vue Logs
    window.stacked_widget.setCurrentWidget(window.page_tracks)
    window.status_label.clicked.emit()
    assert window.stacked_widget.currentWidget() == window.page_logs

    window.close()


def test_logs_view_retranslate_rerenders_rows_in_new_language(temp_db: DatabaseManager, qapp):
    """Un changement de langue à chaud retraduit aussi les lignes déjà affichées (action et niveau)."""
    from amso.core.activity_messages import LogMessage
    from amso.core.i18n import get_i18n

    temp_db.add_activity_log(LogMessage("log.sync_success", {"source": "S1"}), level="SUCCESS", source_name="S1")
    i18n = get_i18n()
    i18n.set_language("fr", save_to_config=False)
    view = LogsView(temp_db)
    view.refresh_logs()
    assert view.table.item(0, 3).text() == "Synchronisation réussie : S1"

    i18n.set_language("en", save_to_config=False)
    view.retranslate_ui()

    assert view.table.item(0, 3).text() == "Synchronization succeeded: S1"
