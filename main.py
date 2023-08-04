from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QVBoxLayout, QLabel, QSizePolicy, \
    QComboBox, QHBoxLayout
from PyQt6.QtGui import QFont, QShortcut, QKeySequence, QPixmap, QPainter
import sys
import json
from camera import Camera
from pygrabber.dshow_graph import FilterGraph

with open("resource/gui_config.json") as f:
    gui_config = json.load(f)
background = gui_config["background"]
label_background = gui_config["label_background"]
label_text = gui_config["label_text"]
label_font_size = gui_config["label_font_size"]
button_font_size = gui_config["button_font_size"]
cursor_active = gui_config["cursor_active"]
blink_time_ms = gui_config["blink_time_ms"]
interface_mode = gui_config["interface_mode"]
size_factor = gui_config["size_factor"]

with open("resource/camera_resolutions.json") as f:
    camera_resolutions = json.load(f)


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.title = 'Camera GUI'
        self.setWindowTitle(self.title)
        self.setStyleSheet(f"background-color: {background};")

        # create control buttons
        self.buttonFont = QFont("Arial", button_font_size)

        # get graph to show available cameras:
        self.graph = FilterGraph()

        # create spaceholder for videoWidget:
        self.video_widget = None
        # get screen size
        screen = app.primaryScreen()
        width = screen.size().width()
        height = screen.size().height()
        stretch_factor = int(height / (size_factor * min(width, height) / 10))

        print(f'Screen dimensions --> width: {width},       height: {height}')

        # create labels
        self.labelFont = QFont("Arial", label_font_size)

        self.TopInfoBox = QLabel("Please select a Camera")
        self.TopInfoBox.setStyleSheet(f"background-color: {label_background};"
                                      f"color: {label_text};")
        self.TopInfoBox.setFont(self.labelFont)
        self.TopInfoBox.setWordWrap(True)

        # create take picture button
        self.PictureButton = QPushButton("  Take Picture  ")
        self.PictureButton.setStyleSheet("background-color: #3d8bcd; color: white")
        self.PictureButton.setFont(self.buttonFont)
        self.PictureButton.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)
        self.PictureButton.clicked.connect(self.take_picture)

        # create load camera button
        self.LoadButton = QPushButton("  Load  ")
        self.LoadButton.setStyleSheet("background-color: #3d8bcd; color: white")
        self.LoadButton.setFont(self.buttonFont)
        self.LoadButton.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)
        self.LoadButton.clicked.connect(self.load_camera_feed)

        # create close shortcut
        close_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
        close_shortcut.activated.connect(self.close_app)

        # create combo box for Cameras
        self.configurationComboBox = QComboBox()
        self.configurationComboBox.setStyleSheet("background-color: #3d8bcd; color: white")
        self.configurationComboBox.setFont(self.buttonFont)
        self.configurationComboBox.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)
        self.available_cameras = self.get_all_available_cameras()
        for camera in self.available_cameras:
            self.configurationComboBox.addItem(camera)
        self.configurationComboBox.currentIndexChanged.connect(self.update_resolutions)

        # create combo box for Resolution
        self.resolutionComboBox = QComboBox()
        self.resolutionComboBox.setStyleSheet("background-color: #3d8bcd; color: white")
        self.resolutionComboBox.setFont(self.buttonFont)
        self.resolutionComboBox.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)
        camera_name = self.configurationComboBox.currentText()
        self.resolutions = camera_resolutions.get(camera_name, {}).get("resolutions", [1920, 1080])
        for resolution in self.resolutions:
            self.resolutionComboBox.addItem(f'{resolution[0]} x {resolution[1]}')

        # top strip layout
        top_layout = QHBoxLayout()
        top_layout.setSpacing(0)
        top_layout.addWidget(self.TopInfoBox, stretch=10)
        top_layout.addWidget(self.configurationComboBox, stretch=1)
        top_layout.addWidget(self.resolutionComboBox, stretch=1)
        top_layout.addWidget(self.LoadButton, stretch=1)
        top_layout.addWidget(self.PictureButton, stretch=1)

        # middle strip layout
        self.middle_layout = QHBoxLayout()
        self.middle_layout.setSpacing(0)
        self.middle_layout.addWidget(self.video_widget, stretch=8)

        # complete layout
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(top_layout, stretch=1)
        layout.addLayout(self.middle_layout, stretch=stretch_factor)
        self.setLayout(layout)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        self.show()

    def update_resolutions(self):
        # Clear the current items in the resolutionComboBox
        self.resolutionComboBox.clear()

        # Get the current camera
        camera_name = self.configurationComboBox.currentText()

        # Get the resolutions for this camera
        resolutions = camera_resolutions.get(camera_name, {}).get("resolutions", [1920, 1080])

        # Add the resolutions to the resolutionComboBox
        for resolution in resolutions:
            self.resolutionComboBox.addItem(f'{resolution[0]} x {resolution[1]}')

    def load_camera_feed(self):
        # removing old video_widget, to free up space
        self.middle_layout.removeWidget(self.video_widget)
        # create new video_widget
        current_camera = self.configurationComboBox.currentText()
        device_number = self.graph.get_input_devices().index(current_camera)
        current_resolution = self.resolutions[self.resolutionComboBox.currentIndex()]
        self.video_widget = VideoWidget(self, device_number, current_resolution)
        # add new video_widget to the middle layout and start the video feed
        self.middle_layout.addWidget(self.video_widget, stretch=8)
        self.video_widget.start_camera_feed()
        self.layout().update()

    def get_all_available_cameras(self):
        return self.graph.get_input_devices()

    def take_picture(self):
        camera_name = self.configurationComboBox.currentText().split(" ")
        self.video_widget.camera_feed.capture_image(camera_name[0])

    def closeEvent(self, event):
        # gets triggered when the close button is clicked.
        self.close_app()
        event.accept()

    def close_app(self):
        """stop all threads and close App"""
        self.close()
        self.video_widget.close_camera()


class VideoWidget(QWidget):
    def __init__(self, parent, device_number, resolution):
        super().__init__(parent)
        self.windowId = self.winId()
        self.device_number = device_number
        self.resolution = resolution
        self.setStyleSheet(f"background-color: {background};")
        self.camera_feed = Camera(self.device_number, self.resolution)
        self.current_frame = QPixmap()
        self.camera_feed.frame_signal.connect(self.update_frame)

    def start_camera_feed(self):
        self.camera_feed.start_camera_feed()

    def close_camera(self):
        self.camera_feed.stop_camera()
        print(f'camera object closed')

    def update_frame(self, frame):
        self.current_frame = frame
        self.update()  # Trigger a call to paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.current_frame)


def main():
    app = QApplication(sys.argv)
    window = MainWindow(app)
    # window.video_widget.start_camera_feed()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
