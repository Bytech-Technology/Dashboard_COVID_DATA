from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QPropertyAnimation, pyqtProperty
from utils.helpers import human_format

class KPIWidget(QtWidgets.QFrame):
    def __init__(self, title, value=0):
        super().__init__()
        self.setObjectName("kpiCard")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(2)

        self.lbl_title = QtWidgets.QLabel(title)
        self.lbl_title.setObjectName("kpiTitle")
        self.lbl_value = QtWidgets.QLabel(human_format(value))
        self.lbl_value.setObjectName("kpiValue")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addStretch()

        self._value = value
        self.anim = QPropertyAnimation(self, b"value")
        self.anim.setDuration(800)
        self.anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

    def getValue(self):
        return self._value

    def setValue(self, val):
        self._value = val
        self.lbl_value.setText(human_format(int(val)))

    value = pyqtProperty(float, fget=getValue, fset=setValue)

    def set_value(self, val):
        self.anim.stop()
        self.anim.setStartValue(self._value)
        self.anim.setEndValue(val)
        self.anim.start()
