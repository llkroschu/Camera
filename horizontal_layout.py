from PyQt6.QtWidgets import QVBoxLayout, QSlider, QLabel, QPushButton, QButtonGroup, QHBoxLayout
from PyQt6.QtCore import Qt

def create_top_layout(main_window):
    self.TopInfoBox = QLabel("Please select a Camera")
    self.TopInfoBox.setStyleSheet(f"background-color: {label_background};"
                                  f"color: {label_text};")
    self.TopInfoBox.setFont(self.labelFont)
    self.TopInfoBox.setWordWrap(True)
    self.logging = LogWidget()
    LogWidget.initialize(self.TopInfoBox)
    self.logging.set_info('Please choose a Camera and Resolution')

    # create take picture button
    self.PictureButton = QPushButton()
    self.PictureButton.setIcon(QIcon('./camera_icon.png'))
    self.PictureButton.setIconSize(QSize(70, 70))
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

    # Dropdown for selecting camera type
    self.camera_type_dropdown = QComboBox()
    self.camera_type_dropdown.setStyleSheet("background-color: #3d8bcd; color: white")
    self.camera_type_dropdown.setFont(self.buttonFont)
    self.camera_type_dropdown.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding)
    self.camera_type_dropdown.addItems(["choose camera", "Baumer Camera", "AlliedVision Camera"])
    self.camera_type_dropdown.currentTextChanged.connect(self.on_camera_type_changed)

    # create combo box for Cameras
    self.configurationComboBox = QComboBox()
    self.configurationComboBox.setStyleSheet("background-color: #3d8bcd; color: white")
    self.configurationComboBox.setFont(self.buttonFont)
    self.configurationComboBox.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding)
    self.get_available_cameras()
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
    resolutions = camera_resolutions.get(camera_name, {}).get("resolutions", [1920, 1080])
    for resolution in resolutions:
        self.resolutionComboBox.addItem(f'{resolution[0]} x {resolution[1]}')

    # top strip layout
    top_layout = QHBoxLayout()
    top_layout.setSpacing(0)
    top_layout.addWidget(self.TopInfoBox, stretch=10)
    top_layout.addWidget(self.camera_type_dropdown, stretch=1)
    top_layout.addWidget(self.configurationComboBox, stretch=1)
    top_layout.addWidget(self.resolutionComboBox, stretch=1)
    top_layout.addWidget(self.LoadButton, stretch=1)
    top_layout.addWidget(self.PictureButton, stretch=1)