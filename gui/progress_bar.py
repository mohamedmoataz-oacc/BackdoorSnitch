from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QColor, QFont


class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0  # Progress value (0–100)
        self.setMinimumSize(250, 250)  # Bigger default size

    def setValue(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        width = self.width()
        height = self.height()

        pen_thickness = 25
        margin = pen_thickness // 2 + 2  # Padding to avoid clipping

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background circle
        bg_pen = QPen(QColor(50, 50, 50), pen_thickness)
        painter.setPen(bg_pen)
        painter.drawEllipse(margin, margin, width - 2 * margin, height - 2 * margin)

        # Draw progress arc
        progress_pen = QPen(QColor(7, 195, 0), pen_thickness)
        painter.setPen(progress_pen)
        rect = QRectF(margin, margin, width - 2 * margin, height - 2 * margin)
        start_angle = -90 * 16
        span_angle = -self.value * 3.6 * 16
        painter.drawArc(rect, start_angle, span_angle)

        # Draw centered percentage text
        painter.setPen(QColor(0, 0, 0))
        font = QFont()
        font.setPointSize(int(width / 10))  # Scales with widget size
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{self.value}%")

        painter.end()
