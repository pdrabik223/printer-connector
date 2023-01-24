import threading
from typing import Union

from printer_device_connector.device_mock import PrinterDeviceMock
from printer_device_connector.marlin_device import MarlinDevice
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)
import sys

from gui_tools.gui_buttons import PrinterHeadPositionController, StartStopContinueButton, TwoParamInput, RecalculatePath
from gui_tools.gui_plots import *
from hapmd.src.hameg_ci import set_up_hamed_device
from pass_generators.scan_loop import main_loop

DEBUG_MODE = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.innit_ui()

        self.thread = None
        self.printer: Union[MarlinDevice, PrusaDevice, PrinterDeviceMock] = None
        self.analyzer = None

        self.measurement_path = None

        if DEBUG_MODE:
            self.printer: PrinterDeviceMock = PrinterDeviceMock.connect_on_port("COM5")
        else:
            self.printer: MarlinDevice = MarlinDevice.connect_on_port("COM5")

        self.analyzer = set_up_hamed_device(debug=DEBUG_MODE)

    def innit_ui(self):

        self._measurements_plot_canvas = None
        self._path_plot_canvas = None
        self._path_2d_plot_canvas = None

        self.setWindowTitle("MDMA gui")
        self._left_wing = QVBoxLayout()
        self._right_wing = QVBoxLayout()
        self._graphs_layout = QHBoxLayout()
        self._graphs_settings_layout = QHBoxLayout()

        self.printer_head_controller = PrinterHeadPositionController()

        self.printer_head_controller.forward.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.FORWARD))

        self.printer_head_controller.up.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.UP))

        self.printer_head_controller.left.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.LEFT))

        self.printer_head_controller.home.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.HOME))

        self.printer_head_controller.right.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.RIGHT))

        self.printer_head_controller.back.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.BACK))

        self.printer_head_controller.down.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.DOWN))

        self.printer_head_controller.center_extruder.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.CENTER))

        self._left_wing.addWidget(self.printer_head_controller)

        self.add_plots()

        self.path_generation_position = TwoParamInput("x:", "y:")
        self.path_generation_size = TwoParamInput("width:", "height:")

        self.path_generation_position.on_editing_finished_connect(self.update_path)
        self.path_generation_size.on_editing_finished_connect(self.update_path)

        self._left_wing.addWidget(self.path_generation_position)
        self._left_wing.addWidget(self.path_generation_size)

        self.recalculate_path = RecalculatePath()
        self._left_wing.addWidget(self.recalculate_path)

        self.start_stop_measurement_button = StartStopContinueButton()
        self.start_stop_measurement_button.pressed.connect(self.start_thread)

        self._left_wing.addWidget(self.start_stop_measurement_button)

        self._left_wing.addWidget(self.start_stop_measurement_button)

        self._central_layout = QHBoxLayout()

        self._right_wing.addLayout(self._graphs_settings_layout)
        self._right_wing.addLayout(self._graphs_layout)

        self._central_layout.addLayout(self._left_wing)
        self._central_layout.addLayout(self._right_wing)

        widget = QWidget()
        widget.setLayout(self._central_layout)
        self.setCentralWidget(widget)

    def update_path(self):

        print(self.path_generation_position.get_vals())
        print(self.path_generation_size.get_vals())

    def move_extruder(self, direction: PrinterHeadPositionController.Direction):
        print(f"moving extruder: {direction}, current position: {self.printer.current_position.to_tuple()}")

        new_position = self.printer.current_position

        if direction == PrinterHeadPositionController.Direction.UP:
            new_position.z += 1

        elif direction == PrinterHeadPositionController.Direction.DOWN:
            new_position.z -= 1

        elif direction == PrinterHeadPositionController.Direction.RIGHT:
            new_position.x += 1

        elif direction == PrinterHeadPositionController.Direction.LEFT:
            new_position.x -= 1

        elif direction == PrinterHeadPositionController.Direction.FORWARD:
            new_position.y += 1

        elif direction == PrinterHeadPositionController.Direction.BACK:
            new_position.y -= 1

        elif direction == PrinterHeadPositionController.Direction.HOME:
            self.printer.send_and_await("G28")
            print(f"new position: {self.printer.current_position.to_tuple()}")
            return
        elif direction == PrinterHeadPositionController.Direction.CENTER:
            if self.printer.current_position.z < 10:
                new_position.z = 10
                self.printer.send_and_await(
                    f"G1 X {self.printer.current_position.x} Y {self.printer.current_position.y} Z {new_position.z}")

            self.printer.send_and_await(
                f"G1 X {self.printer.x_size / 2} Y {self.printer.y_size / 2} Z {new_position.z}")

            print(f"new position: {self.printer.current_position.to_tuple()}")
            return

        self.printer.send_and_await(
            f"G1 X {new_position.x} Y {new_position.y} Z {new_position.z}")

        print(f"new position: {self.printer.current_position.to_tuple()}")

    def add_plots(self) -> None:
        def helper(plot):
            self._graphs_layout.addWidget(plot)

            # toolbar = NavigationToolbar(plot, self)
            # self._graphs_settings_layout.addWidget(toolbar)

        self._path_plot_canvas = PathPlotCanvas()
        helper(self._path_plot_canvas)

        # self._path_2d_plot_canvas = Path2DPlotCanvas()
        # helper(self._path_2d_plot_canvas)

        self._measurements_plot_canvas = MeasurementsPlotCanvas()
        helper(self._measurements_plot_canvas)

    @property
    def path_plot_canvas(self) -> PathPlotCanvas:
        return self._path_plot_canvas

    @property
    def measurements_plot_canvas(self) -> MeasurementsPlotCanvas:
        return self._measurements_plot_canvas

    def check_for_stop(self):

        return (
                self.start_stop_measurement_button.state
                != StartStopContinueButton.State.STOP
        )

    def start_thread(self):
        if self.thread is not None:
            print("thread is already running")
            self.thread.join()
            print("thread is closed")
            self.thread = None
            self.printer_head_controller.enable()
            self.recalculate_path.enable()
            return

        self.printer_head_controller.disable()
        self.recalculate_path.disable()

        printer_size = (80, 80, 80)
        antenna_offset = (5, 52, 0)
        antenna_measurement_radius = 2
        pass_height = 4

        path, no_bins = simple_pass_3d(
            printer_size=printer_size,
            antenna_measurement_radius=antenna_measurement_radius,
            antenna_offset=antenna_offset,
            pass_height=pass_height,
        )

        self.path_plot_canvas.plot_data(
            path,
            printer_boundaries=printer_size,
            antenna_offset=antenna_offset,
            antenna_measurement_radius=antenna_measurement_radius,
        )

        self.measurements_plot_canvas.plot_data(path, measurements=[])

        self.path_plot_canvas.draw()
        self.measurements_plot_canvas.draw()

        print("startup procedure")

        self.thread = threading.Thread(
            target=main_loop,
            args=(
                self,
                path,
                self.printer,
                self.analyzer,
                antenna_offset,
                printer_size,
                antenna_measurement_radius,
            ),
        )
        self.thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
