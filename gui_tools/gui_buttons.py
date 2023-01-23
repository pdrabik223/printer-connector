import enum
from typing import List

from PyQt6.QtWidgets import QPushButton, QGridLayout, QWidget, QVBoxLayout


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
        self.update_background_color(color='rgb(160,160,160)')

    def enable(self):

        for button in self.all_buttons():
            button.blockSignals(False)
        self.update_background_color(color='rgb(98,170,252)')

    def update_background_color(self, color: str = 'rgb(160,160,160)'):
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
        self.setStyleSheet(
            "border-style: outset;"
            "border-width: 2px;"
            "border-radius: 10px;"
            "border-color: beige;"
            "min-width: 10em;"
            "padding: 6px;"
            f"background-color: {STATE_MAPPING[self.state]['color']};"
            "color : beige "

        )

    def change_state(self):
        if self.state == StartStopContinueButton.State.START:
            self.state = StartStopContinueButton.State.STOP

        # elif self.state == StartStopContinueButton.State.STOP:
        #     self.state = StartStopContinueButton.State.CONTINUE
        #
        # elif self.state == StartStopContinueButton.State.CONTINUE:
        #     self.state = StartStopContinueButton.State.STOP

        else:
            self.state = StartStopContinueButton.State.START
        self.update_text()
