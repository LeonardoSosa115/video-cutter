from PySide6.QtCore import QObject, Signal, Slot

from video_processor import cut_video


class CutWorker(QObject):

    finished = Signal()
    error = Signal(str)

    def __init__(self, input_path, output_path, start, end):
        super().__init__()

        self.input_path = input_path
        self.output_path = output_path
        self.start = start
        self.end = end

    @Slot()
    def run(self):
        try:
            cut_video(
                self.input_path,
                self.output_path,
                self.start,
                self.end
            )

            self.finished.emit()

        except FileNotFoundError:
            self.error.emit(
                "No se encontró FFmpeg. Comprueba que esté instalado "
                "y agregado al PATH."
            )

        except Exception as error:
            self.error.emit(str(error))