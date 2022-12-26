import copy
import enum
import threading
from typing import List, Tuple
from device_connector.marlin_device import MarlinDevice
from device_connector.prusa_device import PrusaDevice
import time

import PySimpleGUI as sg


class ExtruderMovement(str, enum.Enum):
    UP = "up"
    DOWN = "down"
    STAY = "stay"


def window_loop(vars):
    window = sg.Window(
        title="Mouse Controller",
        layout=[
            [
                sg.Text(
                    text="Left to lower extruder\nRight to raise extruder",
                    justification="center",
                )
            ]
        ],
        size=(400, 400),
        element_justification="center",
        finalize=True,
        resizable=True,
    )

    window.bind("<Button-1>", "<Button-1>")
    window.bind("<Button-3>", "<Button-3>")

    window.bind("<ButtonRelease-1>", "<ButtonRelease-1>")
    window.bind("<ButtonRelease-3>", "<ButtonRelease-3>")

    window.bind("<Motion>", "<Motion>")

    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button

        if event == "OK" or event == sg.WIN_CLOSED:
            break

        if event == "<Button-1>":
            vars[0] = ExtruderMovement.UP

        if event == "<ButtonRelease-1>":
            vars[0] = ExtruderMovement.STAY

        if event == "<Button-3>":
            vars[0] = ExtruderMovement.DOWN

        if event == "<ButtonRelease-3>":
            vars[0] = ExtruderMovement.STAY

        if event == "<Motion>":
            x = window.mouse_location()[0] - window.current_location()[0]
            y = window.mouse_location()[1] - window.current_location()[1] - 30

            vars[1] = x / window.size[0]
            vars[2] = y / window.size[1]

            if vars[1] < 0:
                vars[1] = 0
            if vars[1] > 1:
                vars[1] = 1

            if vars[2] < 0:
                vars[2] = 0
            if vars[2] > 1:
                vars[2] = 1

    window.close()


if __name__ == "__main__":
    # printer = MarlinDevice.connect()

    vars = [ExtruderMovement.STAY, 0, 0]
    previous_vars = copy.deepcopy(vars)

    height = 0
    previous_height = copy.copy(height)

    x = threading.Thread(
        target=window_loop,
        args=(vars,),
    )
    x.start()

    while x.isAlive():
        if previous_vars != vars or height != previous_height:

            previous_vars = copy.deepcopy(vars)

            print(
                f"direction: {str(vars[0])} position x: {vars[1]} position y: {vars[2]} height: {height}                             \r",
                end="",
            )

        if vars[0] == ExtruderMovement.STAY:
            pass

        if vars[0] == ExtruderMovement.UP:
            height += 1

        if vars[0] == ExtruderMovement.DOWN:
            height -= 1

        time.sleep(0.1)
    print("")
