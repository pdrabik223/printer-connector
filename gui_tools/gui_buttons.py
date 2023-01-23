import threading
from time import sleep
from random import random
from typing import Union

from device_connector.device_mock import DeviceMock
from device_connector.marlin_device import MarlinDevice
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QLineEdit,
    QDialog,
    QGridLayout,
)
import sys
from gui_tools.gui_plots import *
from hapmd.src.hameg3010.hameg3010device import Hameg3010Device
from hapmd.src.hameg3010.hameg3010device_mock import Hameg3010DeviceMock
from hapmd.src.hameg_ci import set_up_hamed_device, get_level
from pass_generators.scan_loop import DEBUG_MODE, main_loop


class PrinterHeadPositionControler(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = QGridLayout()

        self.forward = QPushButton("y+")
        self.up = QPushButton("z+")
        self.mainLayout.addWidget(self.forward, 0, 1)
        self.mainLayout.addWidget(self.up, 0, 2)

        self.left = QPushButton("x-")
        self.home = QPushButton("H")
        self.right = QPushButton("x+")

        self.mainLayout.addWidget(self.left, 1, 0)
        self.mainLayout.addWidget(self.home, 1, 1)
        self.mainLayout.addWidget(self.right, 1, 2)

        self.backward = QPushButton("y-")
        self.down = QPushButton("z-")
        self.mainLayout.addWidget(self.backward, 2, 1)
        self.mainLayout.addWidget(self.down, 2, 2)

        self.setLayout(self.mainLayout)
        self.show()


class StartStopContinueButton(QPushButton):
    START_MEASUREMENT = ("START", "rgb(0, 255,0 )")
    STOP_MEASUREMENT = ("STOP", "rgb(255, 0, 0)")
    CONTINUE_MEASUREMENT = ("CONTINUE", "rgb(0, 0, 255)")

    def __init__(self):
        super().__init__()
        self.start_stop_measurement_button = QPushButton()

        self._state = self.START_MEASUREMENT

        self.start_stop_measurement_button.setText(self.state_text)
        self.start_stop_measurement_button.setStyleSheet(f"background-color:  {self.state_color} ;")
        self.start_stop_measurement_button.clicked.connect(self.change_text)

    @property
    def state_text(self):
        return self._state[0]

    @property
    def state_color(self):
        return self._state[1]

    def set_state(self, new_state):
        self._state = new_state
        self.start_stop_measurement_button.setText(self.state_text)
        self.start_stop_measurement_button.setStyleSheet(f"background-color:  {self.state_color} ;")

    def change_text(self):

        if self.state_text == self.START_MEASUREMENT[0]:
            self.set_state(self.STOP_MEASUREMENT)
        elif self.state_text == self.STOP_MEASUREMENT[0]:
            self.set_state(self.CONTINUE_MEASUREMENT)
        else:
            self.set_state(self.START_MEASUREMENT)

    @property
    def clicked(self):
        return self.start_stop_measurement_button.clicked

    @property
    def connect(self):
        return self.connect()
