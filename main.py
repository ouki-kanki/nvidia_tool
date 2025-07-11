import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QIcon


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle('nvidia tool')
window.setGeometry(100, 100, 600, 400)
window.setWindowIcon(QIcon("nvidia.png"))
window.show()

sys.exit(app.exec())
