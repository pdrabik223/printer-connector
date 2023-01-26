import enum
from typing import List, Tuple, Callable

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
    QDialog, QMessageBox
)

from PyQt6.QtWidgets import QPushButton, QGridLayout, QWidget, QVBoxLayout

CYAN_BLUE = "rgb(98,170,252)"
GRAY = "rgb(160,160,160)"


class PrinterHeadPositionController(QWidget):
    class Direction(enum.Enum):
        UP = 0
        DOWN = 1
        LEFT = 2
        RIGHT = 3
        FORWARD = 4
        BACK = 5
        HOME = 6
        CENTER = 7

    def __init__(self):
        super().__init__()

        self.center_layout = QVBoxLayout()
        self._main_layout = QGridLayout()

        self._forward = QPushButton("Y+")

        self._up = QPushButton("Z+")

        self._main_layout.addWidget(self._forward, *(0, 1))
        self._main_layout.addWidget(self._up, *(0, 2))

        self._left = QPushButton("X-")
        self._home = QPushButton("H")
        self._right = QPushButton("X+")

        self._main_layout.addWidget(self._left, *(1, 0))
        self._main_layout.addWidget(self._home, *(1, 1))
        self._main_layout.addWidget(self._right, *(1, 2))

        self._back = QPushButton("Y-")
        self._down = QPushButton("Z-")
        self._main_layout.addWidget(self._back, *(2, 1))
        self._main_layout.addWidget(self._down, *(2, 2))

        self.center_layout.addLayout(self._main_layout)
        self._center_extruder = QPushButton("Center Extruder")
        self.center_layout.addWidget(self._center_extruder)
        self.setLayout(self.center_layout)

        self.enable()

    def all_buttons(self) -> List[QPushButton]:
        return [self._forward,
                self._up,
                self._left,
                self._home,
                self._right,
                self._back,
                self._down,
                self._center_extruder]

    @property
    def forward(self) -> QPushButton:
        return self._forward

    @property
    def up(self) -> QPushButton:
        return self._up

    @property
    def left(self) -> QPushButton:
        return self._left

    @property
    def home(self) -> QPushButton:
        return self._home

    @property
    def right(self) -> QPushButton:
        return self._right

    @property
    def back(self) -> QPushButton:
        return self._back

    @property
    def down(self) -> QPushButton:
        return self._down

    @property
    def center_extruder(self) -> QPushButton:
        return self._center_extruder

    def disable(self):

        for button in self.all_buttons():
            button.blockSignals(True)
        self.update_background_color(color=GRAY)

    def enable(self):

        for button in self.all_buttons():
            button.blockSignals(False)
        self.update_background_color(color=CYAN_BLUE)

    def update_background_color(self, color: str = GRAY):
        for button in self.all_buttons():
            button.setStyleSheet("border-style: outset;"
                                 "border-width: 2px;"
                                 "border-radius: 10px;"
                                 "border-color: beige;"
                                 "min-width: 2em;"
                                 "padding: 6px;"
                                 "color: white;"
                                 f"background-color: {color};")


class StartStopContinueButton(QPushButton):
    class State(enum.Enum):
        START = 0
        STOP = 1
        CONTINUE = 2

    def __init__(self):
        super().__init__()
        self.state = self.State.START
        self.update_text()
        self.pressed.connect(self.change_state)
        # self.clicked.connect(self.start_thread)

    def update_text(self):

        print(f"Button state: {self.state}")
        STATE_MAPPING = {
            self.State.START: {"color": "rgb(40,200,30)", "text": "START"},
            self.State.STOP: {"color": "rgb(200,40,30)", "text": "STOP"},
            self.State.CONTINUE: {"color": "rgb(0,0,255)", "text": "CONTINUE"},
        }

        self.setText(STATE_MAPPING[self.state]["text"])
        self.update_background_color(STATE_MAPPING[self.state]['color'])

    def disable(self):
        self.blockSignals(True)
        self.update_background_color(color=GRAY)

    def enable(self):

        self.blockSignals(False)
        self.update_background_color(color=CYAN_BLUE)

    def update_background_color(self, color: str = GRAY):

        self.setStyleSheet("border-style: outset;"
                           "border-width: 2px;"
                           "border-radius: 10px;"
                           "border-color: beige;"
                           "min-width: 2em;"
                           "padding: 6px;"
                           "color: white;"
                           f"background-color: {color};")

    def change_state(self):
        if self.state == StartStopContinueButton.State.START:
            self.state = StartStopContinueButton.State.STOP

        else:
            self.state = StartStopContinueButton.State.START
        self.update_text()


class TwoParamInput(QWidget):
    def __init__(self, label_a: str, label_b: str, val_a: int = 50, val_b: int = 50):
        super().__init__()
        self._main_layout = QHBoxLayout()

        self.input_label_a = QLabel(label_a)
        self.input_a = QLineEdit()
        self.input_a.setValidator(QIntValidator())
        self.input_a.setMaxLength(3)
        self.input_a.setMaximumWidth(38)
        self.input_a.setText(str(val_a))
        self.input_a.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.input_label_b = QLabel(label_b)
        self.input_b = QLineEdit()
        self.input_b.setValidator(QIntValidator())
        self.input_b.setMaxLength(3)
        self.input_b.setMaximumWidth(38)
        self.input_b.setText(str(val_b))
        self.input_b.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._main_layout.addWidget(self.input_label_a)
        self._main_layout.addWidget(self.input_a)

        self._main_layout.addWidget(self.input_label_b)
        self._main_layout.addWidget(self.input_b)

        self.setLayout(self._main_layout)

    def get_vals(self) -> Tuple[int, int]:
        return int(self.input_a.text()), int(self.input_b.text())

    def set_default(self, vals: Tuple[int, int]):
        self.input_a.setText(str(vals[0]))
        self.input_b.setText(str(vals[1]))


    def on_editing_finished_connect(self, function: Callable):
        self.input_a.editingFinished.connect(function)
        self.input_b.editingFinished.connect(function)


class RecalculatePath(QPushButton):

    def __init__(self):
        super().__init__()
        self.setText("Recalculate path")
        self.update_background_color()

    def disable(self):
        self.blockSignals(True)
        self.update_background_color(color=GRAY)

    def enable(self):
        self.blockSignals(False)
        self.update_background_color(color=CYAN_BLUE)

    def update_background_color(self, color: str = CYAN_BLUE):
        self.setStyleSheet("border-style: outset;"
                           "border-width: 2px;"
                           "border-radius: 10px;"
                           "border-color: beige;"
                           "min-width: 2em;"
                           "padding: 6px;"
                           "color: white;"
                           f"background-color: {color};")


class SavaData(QPushButton):

    def __init__(self):
        super().__init__()
        self.setText("Save data")
        self.update_background_color()
        self.disable()

    def disable(self):
        self.blockSignals(True)
        self.update_background_color(color=GRAY)

    def enable(self):
        self.blockSignals(False)
        self.update_background_color(color=CYAN_BLUE)

    def update_background_color(self, color: str = CYAN_BLUE):
        self.setStyleSheet("border-style: outset;"
                           "border-width: 2px;"
                           "border-radius: 10px;"
                           "border-color: beige;"
                           "min-width: 2em;"
                           "padding: 6px;"
                           "color: white;"
                           f"background-color: {color};")
