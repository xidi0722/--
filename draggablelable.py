from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import  Qt, QMimeData
from PySide6.QtGui import QDrag

class DraggableLabel(QLabel):
    """Custom QLabel subclass to support drag-and-drop functionality."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if (event.position().toPoint() - self.drag_start_position).manhattanLength() >= QApplication.startDragDistance():
                print("開始拖曳")
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(str(self.property("index")))
                drag.setMimeData(mime_data)
                drag.setPixmap(self.pixmap().scaled(50, 50, Qt.KeepAspectRatio))
                drag.exec(Qt.MoveAction)
        super().mouseMoveEvent(event)



    def dragEnterEvent(self, event):
        print("dragEnterEvent 觸發")
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        print("dropEvent 觸發")
        if event.mimeData().hasText():
            print("mimeData.text() =", event.mimeData().text())
            event.acceptProposedAction()
            # 從自己往上找含有 reorder_images 方法的父 widget
            widget = self.parentWidget()
            while widget is not None and not hasattr(widget, 'reorder_images'):
                widget = widget.parentWidget()
            if widget is not None and hasattr(widget, 'reorder_images'):
                from_index = int(event.mimeData().text())
                to_index = self.property("index")
                print("重新排序：來源 index =", from_index, "目的 index =", to_index)
                widget.reorder_images(from_index, to_index)