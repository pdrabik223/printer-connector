import enum

from PyQt6.QtWidgets import QPushButton, QGridLayout, QWidget


class PrinterHeadPositionController(QWidget):
    class Direction(enum.Enum):
        UP = 0,
        DOWN = 1,
        LEFT = 2,
        RIGHT = 3,
        LEFT = 4,
        FORWARD = 5,
        BACK = 6,
        HOME = 7

    def __init__(self):
        super().__init__()
        self.enabled = False
        self._central_layout = QGridLayout()

        self.forward = QPushButton('Y+')
        self.forward.pressed.connect(lambda: print('Y+'))
        self.up = QPushButton('Z+')

        self._central_layout.addWidget(self.forward, *(0, 1))
        self._central_layout.addWidget(self.up, *(0, 2))

        self.left = QPushButton('X-')
        self.home = QPushButton('H')
        self.right = QPushButton('X+')

        self._central_layout.addWidget(self.left, *(1, 0))
        self._central_layout.addWidget(self.home, *(1, 1))
        self._central_layout.addWidget(self.right, *(1, 2))

        self.back = QPushButton('Y-')
        self.down = QPushButton('Z-')
        self._central_layout.addWidget(self.back, *(2, 1))
        self._central_layout.addWidget(self.down, *(2, 2))

        self.setLayout(self._central_layout)

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True


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
            self.State.START: {
                'color': 'rgb(0,255,0)',
                'text': 'START'
            },
            self.State.STOP: {
                'color': 'rgb(255,0,0)',
                'text': 'STOP'
            },
            self.State.CONTINUE: {
                'color': 'rgb(0,0,255)',
                'text': 'CONTINUE'
            }
        }

        self.setText(STATE_MAPPING[self.state]['text'])
        self.setStyleSheet("{border-style: outset;"
                           "border-width: 2px;"
                           "border-radius: 10px;"
                           "border-color: beige;"
                           "/*font: bold 14px;*/"
                           "min-width: 10em;"
                           "padding: 6px;"
                           f"background-color: {STATE_MAPPING[self.state]['color']};"
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
