import copy
import enum
import threading
from printer_device_connector.marlin_device import MarlinDevice
from printer_device_connector.prusa_device import PrusaDevice
import time

import PySimpleGUI as sg


class ExtruderMovement(str, enum.Enum):
    UP = "up  "
    DOWN = "down"
    STAY = "stay"


def window_loop(variables):
    middle_text = sg.Text(
        "Right to raise extruder\nLeft to lower extruder\nx: ?, y: ?",
        justification="center",
    )
    window = sg.Window(
        title="Mouse Controller",
        layout=[
            [sg.VPush()],
            [middle_text],
            [sg.VPush()],
        ],
        size=(400, 400),
        element_justification="c",
        finalize=True,
        resizable=True,
    )

    window.bind("<Button-1>", ExtruderMovement.UP)
    window.bind("<Button-3>", ExtruderMovement.DOWN)

    window.bind("<ButtonRelease-1>", ExtruderMovement.STAY)
    window.bind("<ButtonRelease-3>", ExtruderMovement.STAY)

    window.bind("<Motion>", "<Motion>")

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if isinstance(event, ExtruderMovement):
            variables[0] = event

        if event == "<Motion>":
            x = window.mouse_location()[0] - window.current_location()[0]
            y = window.mouse_location()[1] - window.current_location()[1] - 30

            x = x / window.size[0]
            y = y / window.size[1]

            if x < 0:
                x = 0

            if x > 1:
                x = 1

            if y < 0:
                y = 0

            if y > 1:
                y = 1

            middle_text.update(
                value=f"Right to raise extruder\nLeft to lower extruder\nx: {round(x, 2)}, y: {round(y, 2)}"
            )

            variables[1] = x
            variables[2] = y

    window.close()


if __name__ == "__main__":
    printer = PrusaDevice.connect()

    variables = [ExtruderMovement.STAY, 0, 0]
    height = 0

    previous_vars = None
    previous_height = None

    thread = threading.Thread(
        target=window_loop,
        args=(variables,),
    )
    thread.start()

    while thread.is_alive():
        if previous_vars != variables or height != previous_height:
            previous_vars = copy.deepcopy(variables)
            previous_height = copy.copy(height)
            x = round(variables[1], 2)
            y = round(variables[2], 2)
            z = height
            # print(
            #     f"direction: {str(vars[0])} position x: {x} position y: {y} height: {height}     \r",
            #     end="",
            # )
            printer.send_and_await(f"G1 X{x} Y{y} Z{z}")

        if variables[0] == ExtruderMovement.UP:
            height += 1

        if variables[0] == ExtruderMovement.DOWN and height > 0:
            height -= 1

        time.sleep(0.1)

    print("")
