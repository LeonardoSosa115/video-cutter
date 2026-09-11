import subprocess
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QFrame,
)
from PySide6.QtCore import Qt

from video_processor import cut_video
from ui.video_player import VideoPlayer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.video_path = None

        self.setWindowTitle("Video Cutter")
        self.setMinimumSize(800, 500)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        central_widget.setLayout(main_layout)

        # =========================
        # HEADER
        # =========================

        title = QLabel("Video Cutter")
        title.setObjectName("title")

        subtitle = QLabel("Recorta tus videos de forma rápida y sencilla")
        subtitle.setObjectName("subtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # =========================
        # VIDEO
        # =========================

        video_frame = QFrame()
        video_frame.setObjectName("videoFrame")

        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)

        video_frame.setLayout(video_layout)

        self.video_player = VideoPlayer()

        self.video_player.start_position_changed.connect(
            self.set_start_time
        )

        self.video_player.end_position_changed.connect(
            self.set_end_time
        )

        video_layout.addWidget(self.video_player)

        main_layout.addWidget(video_frame, 1)

        # =========================
        # SELECT VIDEO
        # =========================

        self.select_button = QPushButton("Seleccionar video")
        self.select_button.setObjectName("secondaryButton")
        self.select_button.clicked.connect(self.select_video)

        main_layout.addWidget(
            self.select_button,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        # =========================
        # TIME CONTROLS
        # =========================

        time_frame = QFrame()
        time_layout = QHBoxLayout()

        time_frame.setLayout(time_layout)

        start_container = QVBoxLayout()

        start_label = QLabel("Inicio")
        start_label.setObjectName("inputLabel")

        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("00:00:00")

        start_container.addWidget(start_label)
        start_container.addWidget(self.start_input)

        # Final
        end_container = QVBoxLayout()

        end_label = QLabel("Final")
        end_label.setObjectName("inputLabel")

        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("00:00:00")

        end_container.addWidget(end_label)
        end_container.addWidget(self.end_input)

        time_layout.addLayout(start_container)
        time_layout.addLayout(end_container)

        main_layout.addWidget(time_frame)

        # =========================
        # FOOTER
        # =========================

        footer_layout = QHBoxLayout()

        self.status_label = QLabel("Listo")
        self.status_label.setObjectName("statusLabel")

        self.cut_button = QPushButton("Recortar video")
        self.cut_button.setObjectName("primaryButton")
        self.cut_button.clicked.connect(self.handle_cut)

        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.cut_button)

        main_layout.addLayout(footer_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }

            QWidget {
                color: #f1f1f1;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#subtitle {
                color: #999999;
                font-size: 14px;
            }

            QFrame#videoFrame {
                background-color: #1b1b1b;
                border: 1px solid #303030;
                border-radius: 12px;
            }

            QLabel#videoPlaceholder {
                color: #777777;
                font-size: 16px;
            }

            QLabel#inputLabel {
                color: #aaaaaa;
                font-size: 13px;
                font-weight: 600;
            }

            QLineEdit {
                background-color: #1c1c1c;
                border: 1px solid #353535;
                border-radius: 7px;
                padding: 10px;
                color: #ffffff;
            }

            QLineEdit:focus {
                border: 1px solid #666666;
            }

            QPushButton {
                border-radius: 7px;
                padding: 10px 18px;
                font-weight: 600;
            }

            QPushButton#secondaryButton {
                background-color: #242424;
                border: 1px solid #3a3a3a;
            }

            QPushButton#secondaryButton:hover {
                background-color: #2e2e2e;
            }

            QPushButton#primaryButton {
                background-color: #ffffff;
                color: #111111;
                padding: 11px 24px;
            }

            QPushButton#primaryButton:hover {
                background-color: #dddddd;
            }

            QLabel#statusLabel {
                color: #888888;
            }
        """)

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar video",
            "",
            "Videos (*.mp4 *.mkv *.avi *.mov *.webm)"
        )

        if file_path:
            self.video_path = file_path

            self.video_player.load_video(file_path)

            self.status_label.setText("Video seleccionado")

    def handle_cut(self):
        if not self.video_path:
            QMessageBox.warning(
                self,
                "Error",
                "Primero selecciona un video."
            )
            return

        start = self.video_player.timeline.start_position
        end = self.video_player.timeline.end_position
        duration = self.video_player.timeline.duration

        if duration <= 0:
            QMessageBox.warning(
                self,
                "Error",
                "El video todavía no está listo."
            )
            return

        if start >= end:
            QMessageBox.warning(
                self,
                "Error",
                "El inicio debe ser menor que el final."
            )
            return

        if start < 0 or end > duration:
            QMessageBox.warning(
                self,
                "Error",
                "El rango seleccionado no es válido."
            )
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar video recortado",
            "",
            "MP4 (*.mp4);;Todos los archivos (*)"
        )

        if not output_path:
            return

        start_seconds = start / 1000
        end_seconds = end / 1000

        self.status_label.setText(
            "Recortando..."
        )

        try:
            cut_video(
                self.video_path,
                output_path,
                start_seconds,
                end_seconds
            )

            self.status_label.setText(
                "Video recortado correctamente"
            )

            QMessageBox.information(
                self,
                "Listo",
                "El video fue recortado correctamente."
            )

        except FileNotFoundError:
            self.status_label.setText(
                "FFmpeg no encontrado"
            )

            QMessageBox.critical(
                self,
                "Error",
                "No se encontró FFmpeg.\n\n"
                "Comprueba que esté instalado "
                "y agregado al PATH."
            )

        except subprocess.CalledProcessError as error:
            self.status_label.setText(
                "Error al recortar"
            )

            QMessageBox.critical(
                self,
                "Error",
                "FFmpeg no pudo procesar el video.\n\n"
                f"{error.stderr}"
            )

        except Exception as error:
            self.status_label.setText(
                "Error al recortar"
            )

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo recortar el video.\n\n"
                f"{error}"
            )

        start = self.start_input.text().strip()
        end = self.end_input.text().strip()

        if not start or not end:
            QMessageBox.warning(
                self,
                "Error",
                "Introduce el tiempo de inicio y final."
            )
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar video recortado",
            "",
            "MP4 (*.mp4);;Todos los archivos (*)"
        )

        if not output_path:
            return

        self.status_label.setText("Recortando...")

        try:
            cut_video(
                self.video_path,
                output_path,
                start,
                end
            )

            self.status_label.setText(
                "Video recortado correctamente"
            )

            QMessageBox.information(
                self,
                "Listo",
                "El video fue recortado correctamente."
            )

        except FileNotFoundError:
            self.status_label.setText("FFmpeg no encontrado")

            QMessageBox.critical(
                self,
                "Error",
                "No se encontró FFmpeg.\n\n"
                "Comprueba que esté instalado y agregado al PATH."
            )

        except Exception as error:
            self.status_label.setText("Error al recortar")

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo recortar el video.\n\n{error}"
            )

    def set_start_time(self, milliseconds):
        self.start_input.setText(
            self.format_time(milliseconds)
        )


    def set_end_time(self, milliseconds):
        self.end_input.setText(
            self.format_time(milliseconds)
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