"""Widget de tableau de playlist avec réorganisation par glisser-déposer (Drag & Drop)."""

from __future__ import annotations

from PySide6.QtWidgets import QTableView, QWidget


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
