from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal


class Backend(QObject):
    toggled = pyqtSignal(bool)

    @pyqtSlot(bool)
    def toggle_feature(self, checked):
        self.toggled.emit(checked)
