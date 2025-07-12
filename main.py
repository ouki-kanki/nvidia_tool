import sys, os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QFrame
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QTimer
from gpu_info import NvidiaGPU
from power_setter import PowerSetter


class NvidiaTool(QWidget):
    def __init__(self):
        super().__init__()

        self.gpu = NvidiaGPU()
        self.power_widget = PowerSetter()

        # sends the signal with the new value from power_widget module
        self.power_widget.powerLimitSet.connect(self.update_power_limit_label)
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        self.setWindowIcon(QIcon("assets/nvidia.png"))
        self.setWindowTitle('nvidia tool')
        self.setGeometry(0, 0, 600, 200)

        self.fan_speed_label = QLabel(f"{self.gpu.get_fan_speed_percent()}")
        self.temp_label = QLabel(f"{self.gpu.get_temp()}")
        self.current_watt_label = QLabel(f"{self.gpu.get_power_draw()}")
        self.current_power_limit_label = QLabel(f"{self.gpu.get_current_power_limit()}")

        label_data = [
            ("Gpu Name: ", QLabel(f"{self.gpu.get_name()}"), QIcon("assets/nvidia.png")),
            ("fan speed: ", self.fan_speed_label, QIcon("assets/fan.png")),
            ("temp: ", self.temp_label, QIcon("assets/temp.png")),
            ("watt usage: ", self.current_watt_label, QLabel("watt")),
            ("current power limit: ", self.current_power_limit_label, "")
        ]

        # *** LAYOUTS ***

        # this is the left layout
        info_box = QGroupBox("Gpu info")
        box_layout = QVBoxLayout()

        for title, value, indicator in label_data:
            row_layout = QHBoxLayout()
            title_label = QLabel(title)
            title_label.setFixedWidth(130)

            title_label.setFont(QFont("Arial", 11))
            value.setFont(QFont("Arial", 11))

            row_layout.addWidget(title_label)
            row_layout.addWidget(value)

            line = QFrame()
            line.setFrameShape(QFrame.Shape.VLine)
            row_layout.addWidget(line)

            if indicator:
                if isinstance(indicator, QIcon):
                    icon_label = QLabel()
                    pixmap = indicator.pixmap(16, 16)
                    icon_label.setPixmap(pixmap)
                    row_layout.addWidget(icon_label)
                else:
                    row_layout.addWidget(indicator)

            box_layout.addLayout(row_layout)

        info_box.setLayout(box_layout)

        # this is the right layout
        graphs_box = QGroupBox('sensors')
        graphs_layout = QVBoxLayout()

        graphs_layout.addWidget(QLabel("yoyo"))
        graphs_box.setLayout(graphs_layout)

        # the top layout that contains the info and the sensor graphs on the right

        top_layout = QHBoxLayout()
        top_layout.addWidget(info_box)
        top_layout.addWidget(graphs_box)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.power_widget)

        self.setLayout(main_layout)

    def update_power_limit_label(self, value):
        """ gets the value from the gpu module with signal"""
        self.current_power_limit_label.setText(f"{value}")

    def update_temp(self, value):
        self.temp_label.setText(f"{value}")

    def update_fan_speed_per(self, value):
        self.fan_speed_label.setText(f"{value}")

    def update_current_watt_usage(self, value):
        self.current_watt_label.setText(f"{value}")

    def refresh_all(self):
        self.update_fan_speed_per(self.gpu.get_fan_speed_percent())
        self.update_temp(self.gpu.get_temp())
        self.update_current_watt_usage(self.gpu.get_power_draw())

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(1000)


app = QApplication(sys.argv)
window = NvidiaTool()
window.show()
sys.exit(app.exec())
