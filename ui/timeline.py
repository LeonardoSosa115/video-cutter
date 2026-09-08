from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush
from PySide6.QtWidgets import QWidget


class Timeline(QWidget):

    position_changed = Signal(int)
    start_position_changed = Signal(int)
    end_position_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self.duration = 0
        self.position = 0

        self.start_position = 0
        self.end_position = 0

        self.dragging = None

        self.setMinimumHeight(50)
        self.setMouseTracking(True)

    # --------------------------------------------------
    # DATA
    # --------------------------------------------------

    def set_duration(self, duration):
        self.duration = max(0, duration)

        self.start_position = 0
        self.end_position = self.duration

        self.update()

    def set_position(self, position):
        self.position = max(
            0,
            min(position, self.duration)
        )

        self.update()

    def set_start_position(self, position):
        if self.duration <= 0:
            return

        position = max(
            0,
            min(position, self.duration)
        )

        position = min(
            position,
            self.end_position
        )

        self.start_position = position

        self.start_position_changed.emit(position)

        self.update()

    def set_end_position(self, position):
        if self.duration <= 0:
            return

        position = max(
            0,
            min(position, self.duration)
        )

        position = max(
            position,
            self.start_position
        )

        self.end_position = position

        self.end_position_changed.emit(position)

        self.update()

    # --------------------------------------------------
    # CONVERSIONS
    # --------------------------------------------------

    def position_to_x(self, position):
        if self.duration <= 0:
            return 0

        return int(
            (position / self.duration)
            * self.width()
        )

    def x_to_position(self, x):
        if self.duration <= 0:
            return 0

        x = max(
            0,
            min(x, self.width())
        )

        return int(
            (x / self.width())
            * self.duration
        )

    # --------------------------------------------------
    # PAINTED
    # --------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        track_y = height // 2
        track_height = 8

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            QBrush(self.palette().color(
                self.palette().ColorRole.Mid
            ))
        )

        painter.drawRoundedRect(
            0,
            track_y - track_height // 2,
            width,
            track_height,
            4,
            4
        )

        start_x = self.position_to_x(
            self.start_position
        )

        end_x = self.position_to_x(
            self.end_position
        )

        painter.setBrush(
            QBrush(
                self.palette().color(
                    self.palette().ColorRole.Highlight
                )
            )
        )

        painter.drawRoundedRect(
            start_x,
            track_y - track_height // 2,
            max(1, end_x - start_x),
            track_height,
            4,
            4
        )

        position_x = self.position_to_x(
            self.position
        )

        painter.setPen(
            QPen(
                self.palette().color(
                    self.palette().ColorRole.Text
                ),
                2
            )
        )

        painter.drawLine(
            position_x,
            5,
            position_x,
            height - 5
        )

        self.draw_handle(
            painter,
            start_x,
            track_y
        )

        self.draw_handle(
            painter,
            end_x,
            track_y
        )

    def draw_handle(self, painter, x, y):
        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            QBrush(
                self.palette().color(
                    self.palette().ColorRole.Text
                )
            )
        )

        painter.drawEllipse(
            QPoint(x, y),
            7,
            7
        )

    # --------------------------------------------------
    # MOUSE
    # --------------------------------------------------

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        x = event.position().x()

        start_x = self.position_to_x(
            self.start_position
        )

        end_x = self.position_to_x(
            self.end_position
        )

        if abs(x - start_x) <= 12:
            self.dragging = "start"
            return

        if abs(x - end_x) <= 12:
            self.dragging = "end"
            return

        self.dragging = "position"

        position = self.x_to_position(x)

        self.position = position
        self.position_changed.emit(position)

        self.update()

    def mouseMoveEvent(self, event):
        if self.dragging is None:
            return

        x = event.position().x()

        position = self.x_to_position(x)

        if self.dragging == "start":
            self.set_start_position(position)

        elif self.dragging == "end":
            self.set_end_position(position)

        elif self.dragging == "position":
            self.position = position

            self.position_changed.emit(
                position
            )

            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = None