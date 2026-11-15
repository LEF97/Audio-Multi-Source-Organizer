"""Tests unitaires et UI pour la page Gestion de la bibliothèque > Sources."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from amso.core.config import ConfigManager, get_config_manager
from amso.core.database import DatabaseManager, SourceType, TrackRecord
from amso.core.playlist_parser import ParsedPlaylistEntry


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    assert isinstance(app, QApplication)
    return app


def test_sources_library_summary_aggregates_tracks_playlists_and_errors(tmp_path: Path) -> None:
    """Vérifie l'agrégation DB des pistes, playlists, durées et erreurs de scan."""
    db_path = tmp_path / "test_lib_sources.db"
    db = DatabaseManager(db_path=db_path)

    src1 = db.add_source(SourceType.LOCAL, "Par artiste", str(tmp_path / "artistes"), sync_mode="realtime")
    src2 = db.add_source(SourceType.LOCAL, "_Playlists", str(tmp_path / "playlists"), sync_mode="startup")
    assert src1.id is not None and src2.id is not None

    t1_id = db.upsert_track(
        TrackRecord(
            source_ref=str(tmp_path / "artistes" / "a.flac"),
            source_id=src1.id,
            source_type=SourceType.LOCAL,
            source_path=str(tmp_path / "artistes" / "a.flac"),
            file_name="a.flac",
            folder_path=str(tmp_path / "artistes"),
            duration_seconds=120.0,
        )
    )
    db.upsert_track(
        TrackRecord(
            source_ref=str(tmp_path / "artistes" / "b.flac"),
            source_id=src1.id,
            source_type=SourceType.LOCAL,
            source_path=str(tmp_path / "artistes" / "b.flac"),
            file_name="b.flac",
            folder_path=str(tmp_path / "artistes"),
            duration_seconds=180.0,
        )
    )

    entries = [
        ParsedPlaylistEntry(
            position=1,
            raw_path="a.flac",
            resolved_path=str(tmp_path / "artistes" / "a.flac"),
            title="A",
            duration_seconds=120.0,
            is_missing=False,
        ),
        ParsedPlaylistEntry(
            position=2,
            raw_path="missing.flac",
            resolved_path=str(tmp_path / "artistes" / "missing.flac"),
            title="Missing",
            duration_seconds=60.0,
            is_missing=True,
        ),
    ]
    pl_id = db.upsert_playlist(
        source_id=src1.id,
        file_path=str(tmp_path / "artistes" / "mix.xspf"),
        file_name="mix.xspf",
        folder_path=str(tmp_path / "artistes"),
        format_str="xspf",
        file_mtime=100.0,
        file_size=500,
        entries=entries,
    )
    with db.get_connection() as conn:
        conn.execute(
            "UPDATE playlist_entries SET track_id = ? WHERE playlist_id = ? AND position = 1;",
            (t1_id, pl_id),
        )

    db.add_activity_log(
        action="Scan terminé avec erreurs",
        level="ERROR",
        category="SCAN",
        source_name="_Playlists",
        items_errors=2,
    )

    summaries = db.get_sources_library_summary()
    assert len(summaries) == 2

    s1 = summaries[0]
    assert s1.source.id == src1.id
    assert s1.track_count == 2
    assert s1.track_duration_seconds == pytest.approx(300.0)
    assert len(s1.playlists) == 1
    assert s1.playlists[0].track_count == 2
    assert s1.playlists[0].total_duration_seconds == pytest.approx(180.0)
    assert s1.playlists[0].missing_count == 1
    assert s1.last_scan_errors == 0

    s2 = summaries[1]
    assert s2.source.id == src2.id
    assert s2.track_count == 0
    assert s2.playlists == []
    assert s2.last_scan_errors == 2


def test_config_library_sources_expanded_nodes_roundtrip(tmp_path: Path) -> None:
    """Vérifie la persistance des nœuds dépliés dans ConfigManager."""
    cfg = ConfigManager(config_path=tmp_path / "config.ini")
    assert cfg.get_library_sources_expanded_nodes() == []
    cfg.set_library_sources_expanded_nodes(["source:1", "playlists:1", "source:3"])
    cfg2 = ConfigManager(config_path=tmp_path / "config.ini")
    assert cfg2.get_library_sources_expanded_nodes() == ["source:1", "playlists:1", "source:3"]


def test_library_sources_tree_hides_empty_groups_and_shows_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolate_config: ConfigManager
) -> None:
    """Vérifie l'affichage arborescent, le masquage des groupes vides et les pastilles de statut."""
    from amso.ui.views.main_window import MainWindow

    _ensure_qapp()
    monkeypatch.setenv("AMSO_QSETTINGS_PATH", str(tmp_path / "qt_settings.ini"))

    src_dir = tmp_path / "Musique"
    src_dir.mkdir()
    pl_file = src_dir / "best.xspf"
    pl_file.write_text("<playlist/>", encoding="utf-8")

    db = DatabaseManager(db_path=tmp_path / "ui_test.db")
    src = db.add_source(SourceType.LOCAL, "Musique", str(src_dir), sync_mode="realtime")
    assert src.id is not None
    db.upsert_track(
        TrackRecord(
            source_ref=str(src_dir / "track1.mp3"),
            source_id=src.id,
            source_type=SourceType.LOCAL,
            source_path=str(src_dir / "track1.mp3"),
            file_name="track1.mp3",
            folder_path=str(src_dir),
            duration_seconds=200.0,
        )
    )
    db.upsert_playlist(
        source_id=src.id,
        file_path=str(pl_file),
        file_name="best.xspf",
        folder_path=str(src_dir),
        format_str="xspf",
        file_mtime=100.0,
        file_size=100,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="track1.mp3",
                resolved_path=str(src_dir / "track1.mp3"),
                title="Track 1",
                duration_seconds=200.0,
                is_missing=False,
            )
        ],
    )

    only_files_dir = tmp_path / "OnlyFiles"
    only_files_dir.mkdir()
    src_only = db.add_source(SourceType.LOCAL, "OnlyFiles", str(only_files_dir), sync_mode="startup")
    assert src_only.id is not None
    db.upsert_track(
        TrackRecord(
            source_ref=str(only_files_dir / "song.mp3"),
            source_id=src_only.id,
            source_type=SourceType.LOCAL,
            source_path=str(only_files_dir / "song.mp3"),
            file_name="song.mp3",
            folder_path=str(only_files_dir),
            duration_seconds=65.0,
        )
    )

    win = MainWindow(db=db)
    try:
        win._on_library_sources_clicked()

        assert hasattr(win, "drawer_library_mgmt")
        assert hasattr(win, "btn_library_sources")
        tree = win.tree_library_sources
        assert tree.topLevelItemCount() == 2
        assert "✅" in win.lbl_lib_health_title.text()
        assert win.btn_lib_show_anomalies.isHidden()
        assert not win.lbl_lib_health_details.isHidden()

        item1 = tree.topLevelItem(0)
        assert item1 is not None
        actions_widget = tree.itemWidget(item1, 7)
        assert actions_widget is not None
        assert len(actions_widget.findChildren(type(win.btn_add_source_library))) == 4
        assert item1.toolTip(5) != ""
        assert not tree.expandsOnDoubleClick()
        assert item1.text(2) == "2"
        assert item1.text(3) == "0:06:40"
        assert item1.text(6) == "🟢"
        assert item1.childCount() == 2

        # Sous-nœuds Fichiers (2 boutons : 🔄, 📂) et Playlists (1 bouton : 🔄) / Playlist (3 boutons : 🔄, 📂, 🛠️)
        files_node = item1.child(0)
        pl_group_node = item1.child(1)
        assert files_node is not None and pl_group_node is not None
        assert len(tree.itemWidget(files_node, 7).findChildren(type(win.btn_add_source_library))) == 2
        assert len(tree.itemWidget(pl_group_node, 7).findChildren(type(win.btn_add_source_library))) == 1
        pl_leaf_node = pl_group_node.child(0)
        assert pl_leaf_node is not None
        assert len(tree.itemWidget(pl_leaf_node, 7).findChildren(type(win.btn_add_source_library))) == 3

        item2 = tree.topLevelItem(1)
        assert item2 is not None
        assert item2.text(2) == "1"
        assert item2.text(3) == "0:01:05"
        assert item2.childCount() == 1

        item1.setExpanded(True)
        assert f"source:{src.id}" in get_config_manager().get_library_sources_expanded_nodes()

        from PySide6.QtWidgets import QHeaderView

        for col in range(8):
            assert tree.header().sectionResizeMode(col) == QHeaderView.ResizeMode.Interactive

        # Double-clic sur une source -> bascule vers Lecteur > Bibliothèque sur cette source
        from PySide6.QtCore import Qt

        win._on_lib_sources_item_double_clicked(item1, 0)
        assert win.btn_by_folder.isChecked()
        cur_folder_item = win.folder_tree.currentItem()
        assert cur_folder_item is not None
        assert cur_folder_item.data(0, Qt.ItemDataRole.UserRole)["source_id"] == src.id

        # Vérifie le résumé plafonné à 5 playlists dans les infobulles parentes
        from amso.core.database import PlaylistSummaryRecord

        fake_pls = [
            PlaylistSummaryRecord(
                id=i,
                source_id=src.id,
                name=f"pl_{i}.xspf",
                file_path=str(pl_file),
                format="xspf",
                track_count=2,
                total_duration_seconds=100.0,
                missing_count=i,
                updated_at=None,
            )
            for i in range(1, 7)
        ]
        lines = win._build_playlists_anomaly_lines(fake_pls)
        assert "6 playlist(s)" in lines[0]
        assert sum(1 for ln in lines if ln.startswith("• ")) == 5
        assert "1 autre(s)" in lines[-1]
    finally:
        win.close()


def test_library_sources_anomalies_banner_and_toggle_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolate_config: ConfigManager
) -> None:
    """Vérifie le bandeau compact et le bouton unique basculant entre anomalies et tout afficher."""
    from amso.ui.views.main_window import MainWindow

    _ensure_qapp()
    monkeypatch.setenv("AMSO_QSETTINGS_PATH", str(tmp_path / "qt_settings.ini"))

    healthy_dir = tmp_path / "Saine"
    healthy_dir.mkdir()
    broken_dir = tmp_path / "Cassee"
    broken_dir.mkdir()
    ok_pl = broken_dir / "ok.xspf"
    ok_pl.write_text("<playlist/>", encoding="utf-8")
    broken_pl = broken_dir / "broken.xspf"
    broken_pl.write_text("<playlist/>", encoding="utf-8")

    db = DatabaseManager(db_path=tmp_path / "ui_anomalies.db")
    src_ok = db.add_source(SourceType.LOCAL, "Saine", str(healthy_dir), sync_mode="realtime")
    src_err = db.add_source(SourceType.LOCAL, "Cassee", str(broken_dir), sync_mode="realtime")
    assert src_ok.id is not None and src_err.id is not None

    db.upsert_track(
        TrackRecord(
            source_ref=str(healthy_dir / "good.mp3"),
            source_id=src_ok.id,
            source_type=SourceType.LOCAL,
            source_path=str(healthy_dir / "good.mp3"),
            file_name="good.mp3",
            folder_path=str(healthy_dir),
            duration_seconds=100.0,
        )
    )
    db.upsert_playlist(
        source_id=src_err.id,
        file_path=str(ok_pl),
        file_name="ok.xspf",
        folder_path=str(broken_dir),
        format_str="xspf",
        file_mtime=100.0,
        file_size=100,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="present.mp3",
                resolved_path=str(broken_dir / "present.mp3"),
                title="Present",
                duration_seconds=120.0,
                is_missing=False,
            )
        ],
    )
    db.upsert_playlist(
        source_id=src_err.id,
        file_path=str(broken_pl),
        file_name="broken.xspf",
        folder_path=str(broken_dir),
        format_str="xspf",
        file_mtime=100.0,
        file_size=100,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="missing.mp3",
                resolved_path=str(broken_dir / "missing.mp3"),
                title="Missing",
                duration_seconds=120.0,
                is_missing=True,
            )
        ],
    )

    win = MainWindow(db=db)
    try:
        win._on_library_sources_clicked()

        assert "⚠️" in win.lbl_lib_health_title.text()
        assert "1" in win.lbl_lib_health_title.text()
        assert win.lbl_lib_health_details.isHidden()
        assert win.lbl_lib_health_details.text() == ""
        assert not win.btn_lib_show_anomalies.isHidden()
        assert "anomalies" in win.btn_lib_show_anomalies.text().lower()

        tree = win.tree_library_sources
        assert tree.topLevelItemCount() == 2
        saine_item = tree.topLevelItem(0)
        cassee_item = tree.topLevelItem(1)
        assert saine_item is not None and cassee_item is not None
        assert not saine_item.isHidden()
        assert not cassee_item.isHidden()

        # Clic sur "Afficher les anomalies" -> filtre uniquement sur les anomalies
        win.btn_lib_show_anomalies.click()
        assert "tout afficher" in win.btn_lib_show_anomalies.text().lower()
        assert saine_item.isHidden()
        assert not cassee_item.isHidden()
        assert cassee_item.isExpanded()

        pl_group = cassee_item.child(0)
        assert pl_group is not None and pl_group.isExpanded()
        pl_by_name = {
            pl_group.child(idx).text(0): pl_group.child(idx)
            for idx in range(pl_group.childCount())
            if pl_group.child(idx) is not None
        }
        ok_pl_item = next(item for name, item in pl_by_name.items() if "ok.xspf" in name)
        broken_pl_item = next(item for name, item in pl_by_name.items() if "broken.xspf" in name)
        assert ok_pl_item.isHidden()
        assert not broken_pl_item.isHidden()

        # Clic sur "Tout afficher" -> réinitialise l'affichage par défaut
        win.btn_lib_show_anomalies.click()
        assert "anomalies" in win.btn_lib_show_anomalies.text().lower()
        assert not saine_item.isHidden()
        assert not cassee_item.isHidden()
        assert not ok_pl_item.isHidden()
        assert not broken_pl_item.isHidden()
    finally:
        win.close()
        win.deleteLater()


def test_library_sources_expand_and_collapse_all_buttons(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolate_config: ConfigManager
) -> None:
    """Les boutons tout déplier / tout replier pilotent toute l'arborescence et persistent l'état."""
    from amso.ui.views.main_window import MainWindow

    _ensure_qapp()
    monkeypatch.setenv("AMSO_QSETTINGS_PATH", str(tmp_path / "qt_settings.ini"))

    db = DatabaseManager(db_path=tmp_path / "lib.db")
    src_dir = tmp_path / "Music"
    src_dir.mkdir()
    src = db.add_source(SourceType.LOCAL, "Musique", str(src_dir), sync_mode="manual")
    assert src.id is not None

    track_path = src_dir / "track.mp3"
    db.upsert_track(
        TrackRecord(
            source_ref=str(track_path),
            source_id=src.id,
            source_type=SourceType.LOCAL,
            source_path=str(track_path),
            file_name="track.mp3",
            folder_path=str(src_dir),
            duration_seconds=100.0,
        )
    )
    pl_path = src_dir / "mix.xspf"
    pl_path.write_text("<playlist/>", encoding="utf-8")
    db.upsert_playlist(
        source_id=src.id,
        file_path=str(pl_path),
        file_name="mix.xspf",
        folder_path=str(src_dir),
        format_str="xspf",
        file_mtime=100.0,
        file_size=100,
        entries=[
            ParsedPlaylistEntry(
                position=1,
                raw_path="track.mp3",
                resolved_path=str(track_path),
                title="Track",
                duration_seconds=100.0,
                is_missing=False,
            )
        ],
    )

    win = MainWindow(db=db)
    try:
        win._on_library_sources_clicked()
        tree = win.tree_library_sources
        src_item = tree.topLevelItem(0)
        assert src_item is not None
        assert not src_item.isExpanded()

        win.btn_expand_lib_sources.click()
        assert src_item.isExpanded()
        pl_group = src_item.child(1)
        assert pl_group is not None and pl_group.isExpanded()
        expanded = get_config_manager().get_library_sources_expanded_nodes()
        assert f"source:{src.id}" in expanded
        assert f"playlists:{src.id}" in expanded

        win.btn_collapse_lib_sources.click()
        assert not src_item.isExpanded()
        assert not pl_group.isExpanded()
        assert get_config_manager().get_library_sources_expanded_nodes() == []
    finally:
        win.close()
        win.deleteLater()


def test_library_sources_formats_size_tabs_and_double_click(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, isolate_config: ConfigManager
) -> None:
    """Vérifie la colonne TAILLE, les nœuds par format, l'onglet Bibliothèque et le double-clic format."""
    from amso.ui.views.main_window import MainWindow

    _ensure_qapp()
    monkeypatch.setenv("AMSO_QSETTINGS_PATH", str(tmp_path / "qt_settings.ini"))

    db = DatabaseManager(db_path=tmp_path / "formats.db")
    src_dir = tmp_path / "Audio"
    src_dir.mkdir()
    src = db.add_source(SourceType.LOCAL, "Audio", str(src_dir), sync_mode="manual")
    assert src.id is not None

    for idx, (fname, fmt, dur, sz) in enumerate(
        [
            ("a.flac", "flac", 200.0, 30 * 1024 * 1024),
            ("b.flac", "flac", 100.0, 20 * 1024 * 1024),
            ("c.mp3", "mp3", 180.0, 5 * 1024 * 1024),
        ]
    ):
        db.upsert_track(
            TrackRecord(
                source_ref=str(src_dir / fname),
                source_id=src.id,
                source_type=SourceType.LOCAL,
                source_path=str(src_dir / fname),
                file_name=fname,
                folder_path=str(src_dir),
                format=fmt,
                duration_seconds=dur,
                file_size=sz,
                title=f"Track {idx}",
            )
        )

    summaries = db.get_sources_library_summary()
    assert len(summaries) == 1
    assert summaries[0].track_size_bytes == 55 * 1024 * 1024
    assert [f.format for f in summaries[0].formats] == ["flac", "mp3"]
    assert summaries[0].formats[0].track_count == 2

    win = MainWindow(db=db)
    try:
        win._on_library_sources_clicked()
        tree = win.tree_library_sources
        src_item = tree.topLevelItem(0)
        assert src_item is not None
        assert "55.0 Mo" in src_item.text(4)

        files_item = src_item.child(0)
        assert files_item is not None
        assert files_item.childCount() == 2
        flac_node = files_item.child(0)
        mp3_node = files_item.child(1)
        assert flac_node is not None and "FLAC" in flac_node.text(0)
        assert mp3_node is not None and "MP3" in mp3_node.text(0)
        assert "50.0 Mo" in flac_node.text(4)

        # Bascule vers l'onglet Bibliothèque
        win.btn_lib_tab_library.click()
        assert win.btn_lib_tab_library.isChecked()
        assert tree.topLevelItemCount() == 3
        all_files_root = tree.topLevelItem(0)
        assert all_files_root is not None
        assert all_files_root.text(2) == "3"
        assert "55.0 Mo" in all_files_root.text(4)
        assert all_files_root.text(6) == "🟢"
        assert all_files_root.childCount() == 2

        # Double-clic sur un format -> ouvre Lecteur > Bibliothèque filtré sur .flac
        overview_flac_node = all_files_root.child(0)
        assert overview_flac_node is not None and "FLAC" in overview_flac_node.text(0)
        win._on_lib_sources_item_double_clicked(overview_flac_node, 0)
        assert win.btn_by_folder.isChecked()
        assert win.folder_search_edit.text() == ".flac"
        assert win.folder_table_model.rowCount() == 2
    finally:
        win.close()
        win.deleteLater()
