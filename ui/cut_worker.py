from PySide6.QtCore import QObject, Signal, Slot

from video_processor import cut_video


class CutWorker(QObject):

    progress = Signal(int)
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
                self.end,
                self.progress.emit
            )

            print("WORKER: FFmpeg terminó")

            self.finished.emit()

        except FileNotFoundError:
            print("WORKER: FFmpeg no encontrado")

            self.error.emit(
                "No se encontró FFmpeg. "
                "Comprueba que esté instalado "
                "y agregado al PATH."
            )

        except Exception as error:
            print("WORKER ERROR:", error)

            self.error.emit(str(error))