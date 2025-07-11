import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QTimer
from gpu_info import NvidiaGPU
from power_setter import PowerSetter

app = QApplication(sys.argv)
gpu = NvidiaGPU()
power_widget = PowerSetter()


def update_label(label, getter, suffix=""):
    """
        label: the instance of Qlabel
        getter: the desired method of the gpu instance
        suffix: diff symbol for temp or wattage etc
        """
    try:
        value = getter()
        label.setText(f"{value}{suffix}")
    except Exception as e:
        label.setText(f"Error: {e}")


window = QWidget()
window.setWindowTitle('nvidia tool')
window.setGeometry(0, 0, 600, 200)
window.setWindowIcon(QIcon("nvidia.png"))

mainLayout = QVBoxLayout()
label_layout = QVBoxLayout()

name_label = QLabel(f"{gpu.get_name()}")
fun_percent_label = QLabel(f"{gpu.get_fan_speed_percent()}%")
temp_label = QLabel(f"Temp: {gpu.get_temp()}°C")
watt_usage_label = QLabel(f"power consumption: {gpu.get_power_draw()}w")
current_power_limit_label = QLabel(f"current power limit: {gpu.get_current_power_limit()} watt")

labels_list = [
    name_label,
    fun_percent_label,
    temp_label,
    watt_usage_label,
    current_power_limit_label
]

for label in labels_list:
    label.setFont(QFont("Arial", 12))
    label_layout.addWidget(label)

labelWidget = QWidget()
labelWidget.setLayout(label_layout)

# udpate the current power limit label from the value inside the power_setter module
def update_power_limit_label(value):
    current_power_limit_label.setText(f"current power limit: {value} watt")

power_widget.powerLimitSet.connect(update_power_limit_label)

def refresh_all():
    update_label(temp_label, gpu.get_temp, "°C")
    update_label(watt_usage_label, gpu.get_power_draw, "w")
    update_label(fun_percent_label, gpu.get_fan_speed_percent, "%")


timer = QTimer()
timer.timeout.connect(refresh_all)
timer.start(1000)

mainLayout.addWidget(labelWidget)
mainLayout.addWidget(power_widget)

window.setLayout(mainLayout)
window.show()
window.move(0, 0)

window.show()
QTimer.singleShot(0, lambda: window.move(100, 100))



sys.exit(app.exec())
