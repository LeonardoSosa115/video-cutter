from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
)

from video_processor import cut_video

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Cutter")
        self.setMinimumSize(500, 300)

        self.video_path = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title = QLabel("Video Cutter")
        layout.addWidget(title)

        self.select_button = QPushButton("Seleccionar video")
        self.select_button.clicked.connect(self.select_video)
        layout.addWidget(self.select_button)

        self.video_label = QLabel("Ningún video seleccionado")
        layout.addWidget(self.video_label)

        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Ejemplo: 00:00:30")

        layout.addWidget(QLabel("Inicio:"))
        layout.addWidget(self.start_input)

        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("Ejemplo: 00:01:45")

        layout.addWidget(QLabel("Final:"))
        layout.addWidget(self.end_input)

        self.cut_button = QPushButton("Recortar")
        self.cut_button.clicked.connect(self.handle_cut)
        layout.addWidget(self.cut_button)

        self.status_label = QLabel("Estado: Listo")
        layout.addWidget(self.status_label)

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar video",
            "",
            "Videos (*.mp4 *.mkv *.avi *.mov *.webm)"
        )

        if file_path:
            self.video_path = file_path
            self.video_label.setText(file_path)
            self.status_label.setText("Estado: Video seleccionado")

    def handle_cut(self):
        if not self.video_path:
            QMessageBox.warning(
                self,
                "Error",
                "Primero selecciona un video."
            )
            return

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

        self.status_label.setText("Estado: Recortando...")

        try:
            cut_video(
                self.video_path,
                output_path,
                start,
                end
            )

            self.status_label.setText(
                "Estado: Video recortado correctamente"
            )

            QMessageBox.information(
                self,
                "Listo",
                "El video fue recortado correctamente."
            )

        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Error",
                "No se encontró FFmpeg."
            )

            self.status_label.setText(
                "Estado: FFmpeg no encontrado"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo recortar el video.\n\n{error}"
            )

            self.status_label.setText(
                "Estado: Error al recortar"
            )