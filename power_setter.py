import re
import subprocess
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton
from PyQt6.QtCore import Qt


class PowerSetter(QWidget):
    powerLimitSet = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gpu power limit")
        layout = QVBoxLayout()

        self.label = QLabel("Power limit")
        layout.addWidget(self.label)

        row_layout = QHBoxLayout()

        button = QPushButton("yo")
        button.setCheckable(True)
        row_layout.addWidget(button)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(100)

        max_limit = self.get_max_power_limit()

        if max_limit:
            self.slider.setMaximum(max_limit - 30)
        else:
            self.slider.setMaximum(380)
            self.slider.setEnabled(False)
            self.label.setText("set power is disabled, max limit could not be found")
            self.label.setStyleSheet("color: tomato;")

        self.slider.setValue(250)
        self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.slider.setStyleSheet("""
                QSlider::groove:horizontal {
                                  background: #ddd;
                                  height: 6px;
                                  }


                QSlider::handle:horizontal {
                    background: #2dd691;
                    border: 1px solid #555;
                    width: 7px;
                    margin: -5px 0;
                    border-radius: 3px;
                }

                                  """)
        self.slider.setTickInterval(5)
        self.slider.setSingleStep(5)
        self.slider.valueChanged.connect(self.snap_to_step)
        self.slider.valueChanged.connect(self.update_label)
        row_layout.addWidget(self.slider)

        self.button = QPushButton("Set power limit")
        self.button.clicked.connect(self.set_power_limit)
        row_layout.addWidget(self.button)

        layout.addLayout(row_layout)
        self.setLayout(layout)

    def snap_to_step(self, value):
        step = 5
        snapped = round(value / step) * step
        self.slider.setValue(snapped)

    def update_label(self):
        self.label.setText(f"power limit: {self.slider.value()} w")

    def get_max_power_limit(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "-q", "-d", "POWER"],
                capture_output=True, text=True, check=True
            )
            match = re.search(r"Max Power Limit\s*:\s*([\d.]+) W", result.stdout)
            if match:
                return int(float(match.group(1)))
            return None
        except subprocess.CalledProcessError:
            return None

    def set_power_limit(self):
        value = self.slider.value()
        try:
            subprocess.run(
                ["pkexec", "nvidia-smi", "-pl", str(value)],
                check=True
            )
            self.label.setText(f"Power limit set to: {value} w")
            self.powerLimitSet.emit(value)
        except subprocess.CalledProcessError:
            self.label.setText("Failed to set power limit")
