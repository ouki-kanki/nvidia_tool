from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import QTimer, Qt


class CpuFan(QLabel):
    def __init__(self, image_path, rotation_speed=60, size=20):
        super().__init__()

        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.fan_pixmap = QPixmap(image_path).scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(self.fan_pixmap)
        self.rotation_angle = 0

        self.rotation_timer(rotation_speed)

    def _rotate(self):
        self.rotation_angle = (self.rotation_angle + 5) % 360
        transform = QTransform().rotate(self.rotation_angle)
        rotated_pixmap = self.fan_pixmap.transformed(
            transform, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(rotated_pixmap)

    def rotation_timer(self, rotation_speed):
        self.timer = QTimer()
        self.timer.timeout.connect(self._rotate)
        self.timer.start(rotation_speed)

    def set_rotation_speed(self, fan_speed_percent: int):
        """ values from 0 - 100 """
        # from 0 to 50 return 20
        # from 50 to 100 return 20 to 0
        value = 20
        min_intenval = 5
        if fan_speed_percent >= 50:
            value = value - (fan_speed_percent - 50) / 2.5
            value = max(round(value), min_intenval)
        # print("the mew value", value)
        self.timer.setInterval(value)


