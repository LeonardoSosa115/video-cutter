from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QLabel,
)


class VideoPlayer(QWidget):

    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        self.play_button = QPushButton("▶")
        self.play_button.setFixedWidth(45)
        self.play_button.clicked.connect(self.toggle_play)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(
            self.set_position
        )

        self.time_label = QLabel("00:00 / 00:00")

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.position_slider)
        controls_layout.addWidget(self.time_label)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.video_widget, 1)
        layout.addLayout(controls_layout)

        self.setLayout(layout)

        self.player.positionChanged.connect(
            self.position_changed
        )

        self.player.durationChanged.connect(
            self.duration_changed
        )

    def load_video(self, file_path):
        self.player.setSource(
            QUrl.fromLocalFile(file_path)
        )

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_button.setText("▶")
        else:
            self.player.play()
            self.play_button.setText("⏸")

    def set_position(self, position):
        self.player.setPosition(position)

    def position_changed(self, position):
        self.position_slider.setValue(position)
        self.update_time_label()

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        self.update_time_label()

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
            return f"{hours:02}:{minutes:02}:{seconds:02}"

        return f"{minutes:02}:{seconds:02}"