import sys, os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QGroupBox,
    QSizePolicy, QPushButton
)
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtCore import QTimer, Qt, QUrl
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6_SwitchControl import SwitchControl
from backend import Backend

from gpu_info import NvidiaGPU
from power_setter import PowerSetter
from graphs.temp_graph import TempCanvas
from components.gpu_fan import CpuFan


os.environ["QT_QUICK_CONTROLS_STYLE"] = "org.kde.desktop"

class NvidiaTool(QWidget):
    def __init__(self):
        super().__init__()

        self.gpu = NvidiaGPU()
        self.power_widget = PowerSetter()
        self.backend = Backend()

        self.amd_mode = False
        self.backend.toggled.connect(self.update_amd_mode)
        self.power_widget.powerLimitSet.connect(self.update_power_limit_label)
        self.init_fan_percent = self.gpu.get_fan_speed_percent()

        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        self.setWindowIcon(QIcon(self.get_resource_path("assets/nvidia.png")))
        self.setWindowTitle('nvidia tool')
        self.setGeometry(0, 0, 600, 200)

        self.temp_label = QLabel(f"{self.gpu.get_temp()} °C")
        self.current_watt_label = QLabel(f"{self.gpu.get_power_draw()}")
        self.current_power_limit_label = QLabel(f"{self.gpu.get_current_power_limit()}")
        self.fan_speed_label = QLabel(f"{self.init_fan_percent}")
        self.fan_speed_label.setFixedWidth(37)
        self.cpu_fan_label: CpuFan = CpuFan(self.get_resource_path("assets/gpu_fan.png"))

        # load amd toggle switch
        qml_amd_switch = QQuickWidget()
        qml_amd_switch.engine().addImportPath("/usr/lib/qt6/qml")

        qml_amd_switch.engine().rootContext() \
            .setContextProperty("backend", self.backend)
        qml_amd_switch.setSource(
            QUrl.fromLocalFile('qml_components/switch.qml'))
        qml_amd_switch.setResizeMode(
            QQuickWidget.ResizeMode.SizeRootObjectToView)
        qml_amd_switch.setVisible(True)
        qml_amd_switch.setMinimumSize(120, 30)
        qml_amd_switch.setClearColor(QColor(0, 0, 0, 0))

        # not working
        # qml_amd_switch.setAttribute(
            # Qt.WidgetAttribute.WA_TranslucentBackground)
        # qml_amd_switch.setWindowFlags(Qt.WindowType.FramelessWindowHint)


        label_data = [
            (
                "Gpu Name: ", QLabel(f"{self.gpu.get_name()}"),
                QIcon(self.get_resource_path("assets/nvidia.png"))
                ),
            ("fan speed: ", self.fan_speed_label, self.cpu_fan_label),
            ("temp: ", self.temp_label, QIcon("assets/temp.png")),
            ("watt usage: ", self.current_watt_label, ""),
            ("current power limit: ", self.current_power_limit_label, "")
        ]

        # *** LAYOUTS ***

        # this is the left layout
        info_box = QGroupBox("Gpu info")
        box_layout = QVBoxLayout()

        for title, value, indicator in label_data:
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            title_label = QLabel(title)
            title_label.setFixedWidth(130)

            value.setSizePolicy(
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Preferred)

            title_label.setFont(QFont("Arial", 11))
            value.setFont(QFont("Arial", 11))

            row_layout.addWidget(title_label)
            row_layout.addWidget(value)

            if indicator:
                if isinstance(indicator, QIcon):
                    icon_label = QLabel()
                    pixmap = indicator.pixmap(16, 16)
                    icon_label.setPixmap(pixmap)
                    row_layout.addWidget(icon_label)
                else:
                    row_layout.addWidget(indicator)

            box_layout.addLayout(row_layout)

        test_btn = QPushButton("test")
        test_btn.clicked.connect(self.test)
        box_layout.addWidget(test_btn)
        info_box.setLayout(box_layout)
        # this is the right layout
        graphs_box = QGroupBox('sensors')
        graphs_layout = QVBoxLayout()
        self.create_plot()

        graphs_layout.addWidget(self.temp_canvas)
        graphs_box.setLayout(graphs_layout)

        top_layout = QHBoxLayout()
        top_layout.addWidget(qml_amd_switch)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        mid_layout = QHBoxLayout()
        mid_layout.addWidget(info_box)
        mid_layout.addWidget(graphs_box)

        main_layout = QVBoxLayout()

        main_layout.addLayout(top_layout)
        main_layout.addLayout(mid_layout)
        main_layout.addWidget(self.power_widget)

        self.setLayout(main_layout)

    def test(self):
        self.cpu_fan_label.set_rotation_speed(90)

    def create_plot(self):
        self.temp_canvas = TempCanvas(self, width=3, height=2, dpi=100)

        self.xdata = list(range(6))
        self.ydata = [self.gpu.get_temp()] * 6
        self.temp_canvas.axes.set_ylim(30, 100)
        self.temp_canvas.axes.tick_params(axis='y', labelsize=6)
        self.temp_canvas.axes.tick_params(axis='x', labelsize=4)
        self.temp_canvas.axes.set_ylabel("°C", fontsize=5)
        self.temp_canvas.figure.tight_layout()
        self.temp_canvas.axes.tick_params(axis='x', bottom=False, labelbottom=False)

        self.temp_canvas.axes.grid(True)
        self.temp_canvas.axes.grid(True, color='gray', linestyle='--', linewidth=0.5)
        self.temp_canvas.axes.set_facecolor('#1e1e1e')  # Dark gray or black
        self.temp_canvas.figure.set_facecolor('#121212')  # Even darker
        self.temp_canvas.axes.tick_params(axis='both', colors='white')

        self._plot_ref = None
        self.update_plot()
        self.plot_timer()

    def update_plot(self):
        line_color = 'r' if self.amd_mode else 'g'
        fill_color = 'red' if self.amd_mode else 'lime'
        fill_alpha = 0.3 if not self.amd_mode else 0.2

        self.ydata = self.ydata[1:] + [self.gpu.get_temp()]
        self.temp_canvas.axes.clear()
        self.temp_canvas.axes.grid(True, color='gray', linestyle='--', linewidth=0.5)

        if self._plot_ref is None:
            self._plot_ref, = self.temp_canvas.axes.plot(self.xdata, self.ydata, line_color)
        else:
            self._plot_ref.set_ydata(self.ydata)

        self.temp_canvas.axes.set_ylim(30, 100)
        self.temp_canvas.axes.fill_between(self.xdata, self.ydata, color=fill_color, alpha=fill_alpha)
        self.temp_canvas.draw()

    def plot_timer(self):
        self.pl_timer = QTimer()
        self.pl_timer.setInterval(1000)
        self.pl_timer.timeout.connect(self.update_plot)
        self.pl_timer.start()

    #  ** signals
    def update_amd_mode(self, checked: bool):
        self.amd_mode = checked

        # graph updates every sec. if the switch is toggled update the value
        self.update_plot()

    def update_power_limit_label(self, value):
        """ gets the value from the gpu module with signal"""
        self.current_power_limit_label.setText(f"{value}")

    def update_temp(self, value):
        self.temp_label.setText(f"{value} °C")

    def update_fan_speed_per(self, value):
        # print("init - new value", self.init_fan_percent, value)
        if value != self.init_fan_percent:
            self.cpu_fan_label.set_rotation_speed(value)
        self.fan_speed_label.setText(f"{value} %")

    def update_current_watt_usage(self, value):
        self.current_watt_label.setText(f"{value} w")

    def refresh_all(self):
        new_fan_percent = self.gpu.get_fan_speed_percent()
        self.update_fan_speed_per(new_fan_percent)

        # set the value that is going to be compared with the new value
        # this is used to prevent the animation to run every second even when the value of the fan remains the same
        self.init_fan_percent = new_fan_percent

        self.update_temp(self.gpu.get_temp())
        self.update_current_watt_usage(self.gpu.get_power_draw())

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(1000)

    @staticmethod
    def get_resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def closeEvent(self, event):  # pylint: disable=invalid-name
        try:
            if hasattr(self, "timer"):
                self.timer.stop()

            if hasattr(self, "plot_update_timer"):
                self.plot_update_timer.stop()

            if hasattr(self.gpu, "shutdown"):
                self.gpu.shutdown()

        except Exception as e:
            print(f"cleanup failed: {e}")

        super().closeEvent(event)


app = QApplication(sys.argv)
window = NvidiaTool()
window.show()
sys.exit(app.exec())
