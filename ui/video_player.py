from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSizePolicy
)

from ui.timeline import Timeline


class VideoPlayer(QWidget):

    start_position_changed = Signal(int)
    end_position_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.player.setAudioOutput(
            self.audio_output
        )

        self.video_widget = QVideoWidget()

        self.video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.video_widget.setMinimumHeight(180)

        self.player.setVideoOutput(
            self.video_widget
        )

        self.setMinimumHeight(300)

        self.timeline = Timeline()

        self.timeline.position_changed.connect(
            self.set_position
        )

        self.timeline.start_position_changed.connect(
            self.handle_start_changed
        )

        self.timeline.end_position_changed.connect(
            self.handle_end_changed
        )

        self.play_button = QPushButton("▶")
        self.play_button.setFixedWidth(45)

        self.play_button.clicked.connect(
            self.toggle_play
        )

        self.time_label = QLabel(
            "00:00 / 00:00"
        )

        self.set_start_button = QPushButton(
            "Marcar inicio"
        )

        self.set_end_button = QPushButton(
            "Marcar final"
        )

        self.set_start_button.clicked.connect(
            self.set_start_position
        )

        self.set_end_button.clicked.connect(
            self.set_end_position
        )

        playback_layout = QHBoxLayout()

        playback_layout.addWidget(
            self.play_button
        )

        playback_layout.addWidget(
            self.time_label
        )

        selection_layout = QHBoxLayout()

        selection_layout.addWidget(
            self.set_start_button
        )

        selection_layout.addWidget(
            self.set_end_button
        )

        selection_layout.addStretch()

        layout = QVBoxLayout()

        layout.setContentsMargins(
            0, 0, 0, 0
        )

        layout.addWidget(
            self.video_widget,
            1
        )

        layout.addWidget(
            self.timeline
        )

        layout.addLayout(
            playback_layout
        )

        layout.addLayout(
            selection_layout
        )

        self.setLayout(layout)

        self.player.positionChanged.connect(
            self.position_changed
        )

        self.player.durationChanged.connect(
            self.duration_changed
        )

    # --------------------------------------------------
    # VIDEO
    # --------------------------------------------------

    def load_video(self, file_path):
        self.player.setSource(
            QUrl.fromLocalFile(file_path)
        )

        self.timeline.set_duration(0)

    # --------------------------------------------------
    # PLAYBACK
    # --------------------------------------------------

    def toggle_play(self):
        if (
            self.player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        ):
            self.player.pause()
            self.play_button.setText("▶")

        else:
            self.player.play()
            self.play_button.setText("⏸")

    def set_position(self, position):
        self.player.setPosition(
            position
        )

    def position_changed(self, position):
        self.timeline.set_position(
            position
        )

        self.update_time_label()

    def duration_changed(self, duration):
        self.timeline.set_duration(
            duration
        )

        self.update_time_label()

    # --------------------------------------------------
    # TIMELINE
    # --------------------------------------------------

    def handle_start_changed(self, position):
        self.start_position_changed.emit(
            position
        )

    def handle_end_changed(self, position):
        self.end_position_changed.emit(
            position
        )

    # --------------------------------------------------
    # MARKERS
    # --------------------------------------------------

    def set_start_position(self):
        position = self.player.position()

        self.timeline.set_start_position(
            position
        )

    def set_end_position(self):
        position = self.player.position()

        self.timeline.set_end_position(
            position
        )

    # --------------------------------------------------
    # TIME
    # --------------------------------------------------

    def update_time_label(self):
        position = self.player.position()
        duration = self.player.duration()

        self.time_label.setText(
            f"{self.format_time(position)} / "
            f"{self.format_time(duration)}"
        )

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000

        minutes = seconds // 60
        seconds = seconds % 60

        hours = minutes // 60
        minutes = minutes % 60

        if hours > 0:
            return (
                f"{hours:02}:"
                f"{minutes:02}:"
                f"{seconds:02}"
            )

        return (
            f"{minutes:02}:"
            f"{seconds:02}"
        )