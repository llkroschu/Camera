from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QVBoxLayout, QLabel, QSizePolicy, \
    QComboBox, QHBoxLayout
from PyQt6.QtGui import QIcon, QAction, QFont, QShortcut, QKeySequence  # QAction is now imported from QtGui
from PyQt6.QtCore import Qt
import sys
import json

with open("/home/llans/ai_vision/ressource/gui_config.json") as f:
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

class CameraWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.title = 'Camera GUI'
        self.setWindowTitle(self.title)
        self.setStyleSheet(f"background-color: {background};")

        # setup video widget
        self.videowidget = VideoWidget(parent=self)

        # create control buttons
        self.buttonFont = QFont("Arial", button_font_size)

        # get screen size
        screen = app.primaryScreen()
        width = screen.size().width()
        height = screen.size().height()
        stretch_factor = int(height / (size_factor * min(width, height) / 10))

        # create labels
        self.labelFont = QFont("Arial", label_font_size)

        self.TopInfoBox = QLabel("Please select a Camera")
        self.TopInfoBox.setStyleSheet(f"background-color: {label_background};"
                                      f"color: {label_text};")
        self.TopInfoBox.setFont(self.labelFont)
        self.TopInfoBox.setWordWrap(True)

        # create take picture button
        self.PictureButton = QPushButton("    Take Picture    ")
        self.PictureButton.setStyleSheet("background-color: #3d8bcd; color: white")
        self.PictureButton.setFont(self.buttonFont)
        self.PictureButton.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)
        self.PictureButton.clicked.connect(self.take_picture)

        # create close shortcut
        close_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
        close_shortcut.activated.connect(self.close_app)

        # create combo box
        self.configurationComboBox = QComboBox()
        self.configurationComboBox.setStyleSheet("background-color: #3d8bcd; color: white")
        self.configurationComboBox.setFont(self.buttonFont)
        self.configurationComboBox.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding)
        self.configurationComboBox.addItem("Raspberry V2")

        self.plug_paths = []
        """
        for plugs in os.listdir(os.path.join(ai_vision_dir, "settings")):
            if os.path.isdir(os.path.join(ai_vision_dir, "settings", plugs)):
                for json_file in os.listdir(os.path.join(ai_vision_dir, "settings", plugs)):
                    
                    self.plug_paths.append(os.path.join(ai_vision_dir, "settings", plugs, json_file))
                    """

        # top strip layout
        top_layout = QHBoxLayout()
        top_layout.setSpacing(0)
        top_layout.addWidget(self.TopInfoBox, stretch=10)
        top_layout.addWidget(self.configurationComboBox, stretch=1)
        top_layout.addWidget(self.PictureButton, stretch=1)

        # middle strip layout
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(0)
        middle_layout.addWidget(self.videowidget, stretch=8)

        # complete layout
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(top_layout, stretch=1)
        layout.addLayout(middle_layout, stretch=stretch_factor)
        self.setLayout(layout)

    def take_picture(self):
        print("Button clicked!")  # Define the slot

    def close_app(self):
        """stop all threads and close App"""
        self.close()


class VideoWidget(QWidget):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        self.flip_method = "none"
        self.windowId = self.winId()
        self.setStyleSheet(f"background-color: {background};")

    def setup_pipeline(self):
        self.pipeline = Gst.parse_launch(
            f"intervideosrc channel=v0 timeout=-1 ! videoflip method={self.flip_method} ! xvimagesink")  # rotate-180
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('sync-message::element', self.on_sync_message)

    def on_sync_message(self, bus, msg):
        message_name = msg.get_structure().get_name()
        print(message_name)
        if message_name == 'prepare-window-handle':
            win_id = self.windowId
            assert win_id
            imagesink = msg.src
            imagesink.set_window_handle(win_id)

    def start_pipeline(self):
        self.pipeline.set_state(Gst.State.PLAYING)

    def take_picture(self):
        print("Take Picture")

    def take_video(self):
        print("Take Video")

def main():
    app = QApplication(sys.argv)
    ex = CameraWindow(app)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
