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

        self.was_playing_before_drag = False

        self.timeline = Timeline()

        self.timeline.position_changed.connect(
            self.set_position
        )

        self.timeline.drag_started.connect(
            self.timeline_drag_started
        )

        self.timeline.drag_finished.connect(
            self.timeline_drag_finished
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

        self.player.playbackStateChanged.connect(
            self.playback_state_changed
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
            return

        start = self.timeline.start_position
        end = self.timeline.end_position
        position = self.player.position()

        if position < start or position >= end:
            self.player.setPosition(start)

        self.player.play()

    def playback_state_changed(self, state):
        if (
            state == QMediaPlayer.PlaybackState.PlayingState
        ):
            self.play_button.setText("⏸")
        else:
            self.play_button.setText("▶")

    def set_position(self, position):
        self.player.setPosition(
            position
        )

    def position_changed(self, position):
        self.timeline.set_position(
            position
        )

        self.update_time_label()

        if (
            self.player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
            and self.timeline.end_position > 0
            and position >= self.timeline.end_position
        ):
            self.player.pause()
            self.player.setPosition(
                self.timeline.end_position
            )

    def duration_changed(self, duration):
        self.timeline.set_duration(
            duration
        )

        self.update_time_label()

    def timeline_drag_started(self):
        self.was_playing_before_drag = (
            self.player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        )

        if self.was_playing_before_drag:
            self.player.pause()

    def timeline_drag_finished(self):
        if self.was_playing_before_drag:
            self.player.play()

        self.was_playing_before_drag = False
    # --------------------------------------------------
    # TIMELINE
    # --------------------------------------------------

    def handle_start_changed(self, position):
        self.start_position_changed.emit(
            position
        )

        if self.player.position() < position:
            self.player.setPosition(position)

    def handle_end_changed(self, position):
        self.end_position_changed.emit(
            position
        )

        if self.player.position() >= position:
            if (
                self.player.playbackState()
                == QMediaPlayer.PlaybackState.PlayingState
            ):
                self.player.pause()

            self.player.setPosition(position)

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