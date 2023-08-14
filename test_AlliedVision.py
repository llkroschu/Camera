import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap
from alliedvisioncamera import AlliedVisionCamera


class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Allied Vision Camera Stream")
        self.layout = QVBoxLayout(self)

        # QLabel to display the camera feed
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        # Initialize the camera
        self.camera = AlliedVisionCamera('DEV_1AB22C029517', [1920,1080])
        self.camera.frame_signal.connect(self.update_image)  # Connect the signal to our slot

        # Start the camera stream
        self.camera.start_stream()

    def update_image(self, pixmap: QPixmap):
        """Slot to update the displayed image."""
        self.image_label.setPixmap(pixmap)

    def closeEvent(self, event):
        """Override the closeEvent to stop the camera stream before closing."""
        self.camera.stop_stream()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec())