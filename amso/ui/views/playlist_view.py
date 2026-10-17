"""Vue Liste de Lecture (Playlist) pour AMSO.

Comprend un mini-lecteur en haut avec contrôles complets et miniature de jaquette,
et un tableau détaillé de la file d'attente en dessous.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QSettings, Qt
from PySide6.QtGui import QAction, QCursor, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from amso.core.database import TrackRecord
from amso.core.i18n import tr
from amso.services.player_service import PlayerService, RepeatMode
from amso.ui.models import PlaylistTableModel, format_duration
from amso.ui.views.cover_helper import load_cover_async
from amso.ui.views.player_view import ClickableSlider


class PlaylistTableView(QTableView):
    """Tableau de playlist avec prise en charge complète du Drag & Drop pour réordonner les pistes."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableView.DragDropMode.InternalMove)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)

    def dragEnterEvent(self, event) -> None:
        if event.source() == self:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if event.source() == self:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        if event.source() != self:
            event.ignore()
            return

        selection = self.selectionModel()
        if not selection:
            event.ignore()
            return

        selected_rows = sorted({idx.row() for idx in selection.selectedRows()})
        if not selected_rows:
            event.ignore()
            return

        model = self.model()
        if not hasattr(model, "player") or not model.player:
            event.ignore()
            return

        total_rows = model.rowCount()
        pos = event.position().toPoint()
        drop_index = self.indexAt(pos)

        if drop_index.isValid():
            rect = self.visualRect(drop_index)
            mid_y = rect.top() + rect.height() // 2
            if pos.y() > mid_y:
                target_row = drop_index.row() + 1
            else:
                target_row = drop_index.row()
        else:
            target_row = total_rows

        offset = sum(1 for r in selected_rows if r < target_row)
        new_start = max(0, min(target_row - offset, total_rows - len(selected_rows)))

        model.player.move_tracks(selected_rows, target_row)
        event.accept()

        self.clearSelection()
        for i in range(len(selected_rows)):
            self.selectRow(new_start + i)


class PlaylistView(QWidget):
    """Page Playlist : Mini-lecteur en haut + Tableau de la file d'attente en dessous."""

    def __init__(self, player_service: PlayerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.player = player_service
        self.playlist_model = PlaylistTableModel(self.player, parent=self)

        self._setup_ui()
        self._connect_signals()

        # État initial
        self.update_track_info(self.player.current_track)
        self.update_playback_state("playing" if self.player.is_playing else "stopped")
        self._update_stats_label()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. En-tête de page
        top_bar = QFrame()
        top_bar.setObjectName("topBarFrame")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.lbl_page_title = QLabel(tr("playlist.page_title"))
        self.lbl_page_title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        top_layout.addWidget(self.lbl_page_title)

        top_layout.addStretch()

        self.lbl_playlist_stats = QLabel("")
        self.lbl_playlist_stats.setStyleSheet("color: #94A3B8; font-size: 13px; font-weight: 500; margin-right: 12px;")
        top_layout.addWidget(self.lbl_playlist_stats)

        self.btn_shuffle_below = QPushButton(tr("playlist.btn_shuffle_below"))
        self.btn_shuffle_below.setProperty("class", "secondary-btn")
        self.btn_shuffle_below.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shuffle_below.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #38BDF8;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
                margin-right: 8px;
            }
            QPushButton:hover {
                background-color: #1E293B;
                border-color: #38BDF8;
                color: #7DD3FC;
            }
        """)
        top_layout.addWidget(self.btn_shuffle_below)

        self.btn_clear_playlist = QPushButton(tr("player.btn_clear_playlist"))
        self.btn_clear_playlist.setProperty("class", "secondary-btn")
        self.btn_clear_playlist.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_playlist.setStyleSheet("""
            QPushButton {
                background-color: #20242D;
                color: #EF4444;
                border: 1px solid #333846;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2E1A1A;
                border-color: #EF4444;
                color: #FCA5A5;
            }
        """)
        top_layout.addWidget(self.btn_clear_playlist)

        main_layout.addWidget(top_bar)

        # 2. Bannière Lecteur Compacte en haut
        player_banner = QFrame()
        player_banner.setObjectName("playerBanner")
        player_banner.setStyleSheet("""
            QFrame#playerBanner {
                background-color: #1A1D24;
                border-bottom: 1px solid #282C37;
                padding: 10px 16px;
            }
        """)
        banner_layout = QVBoxLayout(player_banner)
        banner_layout.setContentsMargins(16, 10, 16, 10)
        banner_layout.setSpacing(8)

        # Ligne supérieure : Miniature + Titre + Boutons + Volume
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        # Miniature de pochette
        self.lbl_thumb = QLabel()
        self.lbl_thumb.setFixedSize(56, 56)
        self.lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_thumb.setStyleSheet("border-radius: 8px;")
        top_row.addWidget(self.lbl_thumb)

        # Titre et Artiste
        track_info_layout = QVBoxLayout()
        track_info_layout.setSpacing(2)
        track_info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.lbl_track_title = QLabel(tr("player.no_track"))
        self.lbl_track_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        track_info_layout.addWidget(self.lbl_track_title)

        self.lbl_track_artist = QLabel("")
        self.lbl_track_artist.setStyleSheet("color: #94A3B8; font-size: 12px;")
        track_info_layout.addWidget(self.lbl_track_artist)

        top_row.addLayout(track_info_layout, 1)

        # Contrôles de lecture
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(8)

        self.btn_shuffle = QPushButton("🔀")
        self.btn_shuffle.setFixedSize(32, 32)
        self.btn_shuffle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shuffle.setToolTip(tr("player.btn_shuffle"))
        self._style_mini_button(self.btn_shuffle)
        ctrl_layout.addWidget(self.btn_shuffle)

        self.btn_prev = QPushButton("⏮")
        self.btn_prev.setFixedSize(34, 34)
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setToolTip(tr("player.btn_previous"))
        self._style_mini_button(self.btn_prev, font_size=13)
        ctrl_layout.addWidget(self.btn_prev)

        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setFixedSize(40, 40)
        self.btn_play_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play_pause.setToolTip(tr("player.btn_play"))
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 20px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
        """)
        ctrl_layout.addWidget(self.btn_play_pause)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(32, 32)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setToolTip(tr("player.btn_stop"))
        self._style_mini_button(self.btn_stop, font_size=11)
        ctrl_layout.addWidget(self.btn_stop)

        self.btn_next = QPushButton("⏭")
        self.btn_next.setFixedSize(34, 34)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setToolTip(tr("player.btn_next"))
        self._style_mini_button(self.btn_next, font_size=13)
        ctrl_layout.addWidget(self.btn_next)

        self.btn_repeat = QPushButton("🔁")
        self.btn_repeat.setFixedSize(32, 32)
        self.btn_repeat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_repeat.setToolTip(tr("player.btn_repeat"))
        self._style_mini_button(self.btn_repeat)
        ctrl_layout.addWidget(self.btn_repeat)

        top_row.addLayout(ctrl_layout)

        # Contrôle du volume compact
        vol_layout = QHBoxLayout()
        vol_layout.setSpacing(6)
        vol_layout.setContentsMargins(16, 0, 0, 0)

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(28, 28)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_mini_button(self.btn_mute, font_size=11)
        vol_layout.addWidget(self.btn_mute)

        self.slider_volume = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(self.player.volume)
        self.slider_volume.setFixedWidth(90)
        self.slider_volume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_volume.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background-color: #282C37;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background-color: #38BDF8;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #E2E8F0;
                width: 10px;
                height: 10px;
                margin: -3px 0;
                border-radius: 5px;
            }
        """)
        vol_layout.addWidget(self.slider_volume)

        top_row.addLayout(vol_layout)
        banner_layout.addLayout(top_row)

        # Ligne inférieure : Seekbar
        seek_row = QHBoxLayout()
        seek_row.setSpacing(8)
        seek_row.setContentsMargins(4, 0, 4, 0)

        self.lbl_time_cur = QLabel("00:00")
        self.lbl_time_cur.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: monospace;")
        seek_row.addWidget(self.lbl_time_cur)

        self.slider_seek = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider_seek.setRange(0, 1000)
        self.slider_seek.setValue(0)
        self.slider_seek.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_seek.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 5px;
                background-color: #282C37;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background-color: #0284C7;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #F8FAFC;
                width: 12px;
                height: 12px;
                margin: -3px 0;
                border-radius: 6px;
            }
        """)
        seek_row.addWidget(self.slider_seek, 1)

        self.lbl_time_total = QLabel("00:00")
        self.lbl_time_total.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: monospace;")
        seek_row.addWidget(self.lbl_time_total)

        banner_layout.addLayout(seek_row)
        main_layout.addWidget(player_banner)

        # 3. Tableau de la playlist
        self.table_view = PlaylistTableView()
        self.table_view.setModel(self.playlist_model)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setShowGrid(False)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.setCursor(Qt.CursorShape.PointingHandCursor)

        # Tailles et configuration des colonnes
        header = self.table_view.horizontalHeader()
        header.setSectionsMovable(True)
        header.setStretchLastSection(False)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._on_header_context_menu)

        for idx in range(len(self.playlist_model.COLUMNS)):
            header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Interactive)

        if not self.restore_table_state():
            for idx, col_def in enumerate(self.playlist_model.COLUMNS):
                header.resizeSection(idx, col_def[1])

        header.sectionResized.connect(lambda *_: self.save_table_state())
        header.sectionMoved.connect(lambda *_: self.save_table_state())

        main_layout.addWidget(self.table_view, 1)

    def _style_mini_button(self, btn: QPushButton, font_size: int = 12) -> None:
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #20242D;
                color: #CBD5E1;
                border: 1px solid #282C37;
                border-radius: 4px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #2B303C;
                color: #F8FAFC;
                border-color: #38BDF8;
            }}
            QPushButton:pressed {{
                background-color: #0284C7;
                color: #FFFFFF;
            }}
        """)

    def _connect_signals(self) -> None:
        # Signaux émis par le PlayerService
        self.player.track_changed.connect(self.update_track_info)
        self.player.state_changed.connect(self.update_playback_state)
        self.player.position_changed.connect(self.update_position)
        self.player.volume_changed.connect(self.update_volume)
        self.player.playlist_updated.connect(self._update_stats_label)
        self.player.shuffle_changed.connect(self.update_shuffle_ui)
        self.player.repeat_changed.connect(self.update_repeat_ui)

        # Contrôles utilisateur
        self.btn_play_pause.clicked.connect(self.player.toggle_play_pause)
        self.btn_stop.clicked.connect(self.player.stop)
        self.btn_next.clicked.connect(self.player.next)
        self.btn_prev.clicked.connect(self.player.previous)
        self.btn_shuffle.clicked.connect(self.player.toggle_shuffle)
        self.btn_repeat.clicked.connect(self.player.toggle_repeat)
        self.btn_mute.clicked.connect(self.player.toggle_mute)
        self.btn_shuffle_below.clicked.connect(self._on_shuffle_below_clicked)
        self.btn_clear_playlist.clicked.connect(self.player.clear_playlist)

        # Seekbar
        self.slider_seek.sliderPressed.connect(lambda: self.player.set_seeking(True))
        self.slider_seek.sliderReleased.connect(self._on_seek_released)
        self.slider_seek.sliderMoved.connect(self._on_seek_moved)

        # Volume
        self.slider_volume.valueChanged.connect(self.player.set_volume)

        # Interactions sur le tableau de playlist
        self.table_view.doubleClicked.connect(self._on_table_double_clicked)
        self.table_view.customContextMenuRequested.connect(self._on_context_menu)

        # Synchronisation de l'état initial
        self.update_shuffle_ui(self.player.is_shuffle)
        self.update_repeat_ui(self.player.repeat_mode)
        self.update_volume(self.player.volume, self.player.is_muted)
        self._update_stats_label()
        if self.player.current_track:
            self.update_track_info(self.player.current_track)

    def _on_header_context_menu(self, pos: QPoint) -> None:
        header = self.table_view.horizontalHeader()
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #1A1D24; color: #E2E8F0; border: 1px solid #282C37; padding: 4px; }"
            "QMenu::item:selected { background-color: #0284C7; }"
        )

        act_show_all = QAction(tr("table.menu_show_all"), menu)
        act_show_all.triggered.connect(self._show_all_columns)
        menu.addAction(act_show_all)

        act_reset = QAction(tr("table.menu_reset_columns"), menu)
        act_reset.triggered.connect(self._reset_default_columns)
        menu.addAction(act_reset)

        menu.addSeparator()

        title_act = QAction(f"— {tr('table.menu_columns')} —", menu)
        title_act.setEnabled(False)
        menu.addAction(title_act)

        for col_idx in range(self.playlist_model.columnCount()):
            col_name = self.playlist_model.headerData(col_idx, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            if not col_name or col_name.strip() in ("", "#"):
                continue
            act = QAction(col_name, menu)
            act.setCheckable(True)
            act.setChecked(not self.table_view.isColumnHidden(col_idx))
            act.toggled.connect(lambda checked, c=col_idx: self._toggle_column(c, checked))
            menu.addAction(act)

        menu.exec(header.mapToGlobal(pos))

    def _toggle_column(self, col_idx: int, visible: bool) -> None:
        self.table_view.setColumnHidden(col_idx, not visible)
        self.save_table_state()

    def _show_all_columns(self) -> None:
        for c in range(self.playlist_model.columnCount()):
            self.table_view.setColumnHidden(c, False)
        self.save_table_state()

    def _reset_default_columns(self) -> None:
        header = self.table_view.horizontalHeader()
        for idx, col_def in enumerate(self.playlist_model.COLUMNS):
            self.table_view.setColumnHidden(idx, False)
            header.resizeSection(idx, col_def[1])
            visual_idx = header.visualIndex(idx)
            if visual_idx != idx:
                header.moveSection(visual_idx, idx)
        self.save_table_state()

    def save_table_state(self) -> None:
        """Sauvegarde la configuration des colonnes du tableau de playlist (largeurs, ordre, masquage)."""
        settings = QSettings("AMSO", "AudioMultiSourceOrganizer")
        settings.setValue("header_state_playlist", self.table_view.horizontalHeader().saveState())

    def restore_table_state(self) -> bool:
        """Restaure la configuration des colonnes du tableau de playlist."""
        settings = QSettings("AMSO", "AudioMultiSourceOrganizer")
        state = settings.value("header_state_playlist")
        if state is not None:
            return bool(self.table_view.horizontalHeader().restoreState(state))
        return False

    def _on_seek_released(self) -> None:
        val = self.slider_seek.value()
        ratio = val / 1000.0
        self.player.seek_ratio(ratio)
        self.player.set_seeking(False)

    def _on_seek_moved(self, value: int) -> None:
        track = self.player.current_track
        if track and track.duration_seconds:
            curr_sec = (value / 1000.0) * track.duration_seconds
            self.lbl_time_cur.setText(format_duration(curr_sec))

    def _on_shuffle_below_clicked(self) -> None:
        """Déclenche le mélange des pistes en dessous de la piste en cours et active l'état shuffle."""
        self.player.set_shuffle(True)
        self.player.shuffle_playlist(below_current=True)

    def _on_table_double_clicked(self, index) -> None:
        if index.isValid():
            self.player.play_index(index.row())

    def _on_context_menu(self, pos: QPoint) -> None:
        index = self.table_view.indexAt(pos)
        menu = QMenu(self)

        if index.isValid():
            row = index.row()
            act_play = QAction(tr("playlist.menu_play"), self)
            act_play.triggered.connect(lambda: self.player.play_index(row))
            menu.addAction(act_play)

            act_remove = QAction(tr("playlist.menu_remove"), self)
            act_remove.triggered.connect(lambda: self.player.remove_at(row))
            menu.addAction(act_remove)

            menu.addSeparator()

        if len(self.player.playlist) > 1:
            act_shuffle = QAction(tr("playlist.menu_shuffle_below"), self)
            act_shuffle.triggered.connect(self._on_shuffle_below_clicked)
            menu.addAction(act_shuffle)
            menu.addSeparator()

        act_clear = QAction(tr("playlist.menu_clear"), self)
        act_clear.triggered.connect(self.player.clear_playlist)
        menu.addAction(act_clear)

        menu.exec(QCursor.pos())

    def _update_stats_label(self) -> None:
        tracks = self.player.playlist
        count = len(tracks)
        if count == 0:
            self.lbl_playlist_stats.setText(tr("player.empty_playlist"))
            return

        total_sec = sum(t.duration_seconds or 0 for t in tracks)
        dur_str = format_duration(total_sec)
        key = "playlist.stats_count_singular" if count == 1 else "playlist.stats_count"
        self.lbl_playlist_stats.setText(tr(key, count=f"{count:,}", duration=dur_str))

    def _on_cover_loaded(self, path: str, pixmap: QPixmap) -> None:
        """Appelé dès que la vignette asynchrone a fini de charger."""
        if getattr(self, "_displayed_track_path", None) == path:
            self.lbl_thumb.setPixmap(pixmap)

    def update_track_info(self, track: TrackRecord | None) -> None:
        """Met à jour l'affichage avec la piste en cours de lecture de façon instantanée."""
        track_path = track.source_path if track else ""
        self._displayed_track_path = track_path

        pixmap = load_cover_async(track, size=56, radius=8, callback=self._on_cover_loaded, force_check=True)
        self.lbl_thumb.setPixmap(pixmap)

        if not track:
            self.lbl_track_title.setText(tr("player.no_track"))
            self.lbl_track_artist.setText("")
            self.lbl_time_cur.setText("00:00")
            self.lbl_time_total.setText("00:00")
            self.slider_seek.setValue(0)
            return

        title_text = track.title or track.file_name or tr("track.untitled")
        self.lbl_track_title.setText(title_text)

        artist_part = track.artist or tr("track.unknown_artist")
        album_part = f" — {track.album}" if track.album else ""
        self.lbl_track_artist.setText(f"{artist_part}{album_part}")

        total_sec = track.duration_seconds or 0
        self.lbl_time_total.setText(format_duration(total_sec))

        # Faire défiler la table pour que la ligne active soit visible
        curr_idx = self.player.current_index
        if 0 <= curr_idx < self.playlist_model.rowCount():
            model_idx = self.playlist_model.index(curr_idx, 0)
            self.table_view.scrollTo(model_idx)

    def update_playback_state(self, state: str) -> None:
        if state == "playing":
            self.btn_play_pause.setText("⏸")
            self.btn_play_pause.setToolTip(tr("player.btn_pause"))
            if self.player.current_track:
                load_cover_async(
                    self.player.current_track,
                    size=56,
                    radius=8,
                    callback=self._on_cover_loaded,
                    force_check=True,
                )
        else:
            self.btn_play_pause.setText("▶")
            self.btn_play_pause.setToolTip(tr("player.btn_play"))

    def update_position(self, current_ms: int, total_ms: int, ratio: float) -> None:
        self.lbl_time_cur.setText(format_duration(current_ms / 1000.0))
        if total_ms > 0:
            self.lbl_time_total.setText(format_duration(total_ms / 1000.0))
        val = int(ratio * 1000)
        self.slider_seek.blockSignals(True)
        self.slider_seek.setValue(val)
        self.slider_seek.blockSignals(False)

    def update_volume(self, volume: int, is_muted: bool) -> None:
        self.slider_volume.blockSignals(True)
        self.slider_volume.setValue(volume)
        self.slider_volume.blockSignals(False)

        if is_muted or volume == 0:
            self.btn_mute.setText("🔇")
        else:
            self.btn_mute.setText("🔊")

    def update_shuffle_ui(self, active: bool) -> None:
        if active:
            self.btn_shuffle.setStyleSheet("""
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 4px;
                font-size: 12px;
            """)
        else:
            self._style_mini_button(self.btn_shuffle)

    def update_repeat_ui(self, mode: int) -> None:
        if mode == RepeatMode.OFF:
            self.btn_repeat.setText("🔁")
            self._style_mini_button(self.btn_repeat)
        elif mode == RepeatMode.ALL:
            self.btn_repeat.setText("🔁")
            self.btn_repeat.setStyleSheet("""
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 4px;
                font-size: 12px;
            """)
        elif mode == RepeatMode.ONE:
            self.btn_repeat.setText("🔂")
            self.btn_repeat.setStyleSheet("""
                background-color: #0284C7;
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 4px;
                font-size: 12px;
            """)

    def retranslate_ui(self) -> None:
        """Met à jour l'ensemble des textes, infobulles et en-têtes selon la langue active."""
        self.lbl_page_title.setText(tr("playlist.page_title"))
        if hasattr(self, "btn_shuffle_below"):
            self.btn_shuffle_below.setText(tr("playlist.btn_shuffle_below"))
        self.btn_clear_playlist.setText(tr("player.btn_clear_playlist"))
        self._update_stats_label()

        if not self.player.current_track:
            self.lbl_track_title.setText(tr("player.no_track"))
        else:
            self.update_track_info(self.player.current_track)

        self.btn_shuffle.setToolTip(tr("player.btn_shuffle"))
        self.btn_prev.setToolTip(tr("player.btn_previous"))
        if self.player.is_playing:
            self.btn_play_pause.setToolTip(tr("player.btn_pause"))
        else:
            self.btn_play_pause.setToolTip(tr("player.btn_play"))
        self.btn_stop.setToolTip(tr("player.btn_stop"))
        self.btn_next.setToolTip(tr("player.btn_next"))
        self.btn_repeat.setToolTip(tr("player.btn_repeat"))

        if hasattr(self, "playlist_model"):
            self.playlist_model.notify_language_changed()
