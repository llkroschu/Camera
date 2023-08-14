from PyQt6.QtWidgets import QVBoxLayout, QSlider, QLabel, QPushButton, QButtonGroup, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt


def create_camera_controls(main_window):
    # Create the QVBoxLayout for the right side
    right_layout = QVBoxLayout()

    # Create and add the QSlider for exposure time
    exposure_layout = QHBoxLayout()
    exposure_slider = QSlider(Qt.Orientation.Horizontal)
    exposure_slider.setMinimum(5)  # 0.5 multiplied by 10 to handle float values
    exposure_slider.setMaximum(10000)  # 1000 multiplied by 10
    exposure_slider.setValue(1500)
    exposure_slider_label = QLabel("150")
    exposure_slider.valueChanged.connect(lambda value: exposure_slider_label.setText(str(value / 10)))
    exposure_slider.valueChanged.connect(lambda value:main_window.handle_exposure_setting(value*10))
    exposure_slider.setTickInterval(2500)
    exposure_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
    exposure_label = QLabel("Exposure Time (ms):")
    set_style([exposure_label, exposure_slider, exposure_slider_label], main_window)
    right_layout.addWidget(exposure_label)
    exposure_layout.addWidget(exposure_slider, stretch=7)
    exposure_layout.addWidget(exposure_slider_label, stretch=1)
    right_layout.addLayout(exposure_layout)


    # Create and add the horizontal buttons for Exposure Auto
    exposure_buttons_layout = QHBoxLayout()
    exposure_auto_button_group = QButtonGroup()
    exposure_auto_off = QPushButton("Off")
    exposure_auto_once = QPushButton("Once")
    exposure_auto_continuous = QPushButton("Continuous")
    exposure_auto_off.clicked.connect(main_window.handle_exposure_off)
    exposure_auto_once.clicked.connect(main_window.handle_exposure_once)
    exposure_auto_continuous.clicked.connect(main_window.handle_exposure_continuous)
    exposure_auto_button_group.addButton(exposure_auto_off)
    exposure_auto_button_group.addButton(exposure_auto_once)
    exposure_auto_button_group.addButton(exposure_auto_continuous)
    exposure_buttons_layout.addWidget(exposure_auto_off)
    exposure_buttons_layout.addWidget(exposure_auto_once)
    exposure_buttons_layout.addWidget(exposure_auto_continuous)
    exposure_auto_label = QLabel("Exposure Auto:")
    set_style([exposure_auto_label, exposure_auto_off, exposure_auto_once, exposure_auto_continuous], main_window)
    right_layout.addWidget(exposure_auto_label)
    right_layout.addLayout(exposure_buttons_layout)

    # Create and add the QSlider for gain
    gain_layout = QHBoxLayout()
    gain_slider = QSlider(Qt.Orientation.Horizontal)
    gain_slider.setMinimum(0)
    gain_slider.setMaximum(30)
    gain_slider_label = QLabel("0")
    set_style([gain_slider, gain_slider_label], main_window)
    gain_slider.valueChanged.connect(lambda value: gain_slider_label.setText(str(value)))
    gain_slider.valueChanged.connect(lambda value: main_window.handle_gain_setting(value))
    gain_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
    gain_slider.setTickInterval(5)
    gain_label = QLabel("Gain:")
    set_style([gain_label, gain_slider, gain_slider_label], main_window)
    right_layout.addWidget(gain_label)
    gain_layout.addWidget(gain_slider, stretch=7)
    gain_layout.addWidget(gain_slider_label, stretch=1)
    right_layout.addLayout(gain_layout)

    # Create and add the QSlider for gamma
    gamma_layout = QHBoxLayout()
    gamma_slider = QSlider(Qt.Orientation.Horizontal)
    gamma_slider.setMinimum(-5)  # 0.5 multiplied by 10
    gamma_slider.setMaximum(25)  # 2.5 multiplied by 10
    gamma_slider_label = QLabel("0.5")
    gamma_slider.valueChanged.connect(lambda value: gamma_slider_label.setText(str(value / 10)))
    gamma_slider.valueChanged.connect(lambda value: main_window.handle_gamma_setting(value*10))
    gamma_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
    gamma_slider.setTickInterval(5)
    gamma_label = QLabel("Gamma:")
    set_style([gamma_slider_label, gamma_slider, gamma_label], main_window)
    right_layout.addWidget(gamma_label)
    gamma_layout.addWidget(gamma_slider, stretch=7)
    gamma_layout.addWidget(gamma_slider_label, stretch=1)
    right_layout.addLayout(gamma_layout)

    return right_layout


def set_style(elements, main_window):
    for element in elements:
        element.setStyleSheet("background-color: #3d8bcd; color: white")
        element.setFont(main_window.buttonFont)
        element.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding)

