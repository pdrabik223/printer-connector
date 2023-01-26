import os
import threading
from tkinter.filedialog import asksaveasfile
from typing import Union, Dict

from PyQt6.uic.properties import QtGui

from printer_device_connector.device_mock import PrinterDeviceMock
from printer_device_connector.marlin_device import MarlinDevice
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton, QFileDialog,
)
import sys
import pandas as pd

from gui_tools.gui_buttons import PrinterHeadPositionController, StartStopContinueButton, TwoParamInput, \
    RecalculatePath, SavaData
from gui_tools.gui_plots import *
from hapmd.src.hameg_ci import set_up_hamed_device

from typing import List, Tuple, Union

from printer_device_connector.device_mock import PrinterDeviceMock
from printer_device_connector.marlin_device import MarlinDevice
from printer_device_connector.prusa_device import PrusaDevice
from gui_tools.gui_plots import Point
from hapmd.src.hameg3010.hameg3010device import Hameg3010Device
from hapmd.src.hameg3010.hameg3010device_mock import Hameg3010DeviceMock
from hapmd.src.hameg_ci import get_level

PRINTER_DEBUG_MODE = True
ANALYZER_DEBUG_MODE = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.measurement = None
        self.innit_ui()

        self.path = None
        self.thread = None
        self.printer: Union[MarlinDevice, PrusaDevice, PrinterDeviceMock] = None

        self.antenna_offset = (-52, 0, 0)
        self.antenna_measurement_radius = 2
        self.pass_height = 4

        if PRINTER_DEBUG_MODE:
            self.printer: PrinterDeviceMock = PrinterDeviceMock.connect_on_port("COM5")
        else:
            self.printer: MarlinDevice = MarlinDevice.connect_on_port("COM5")

        self.analyzer = set_up_hamed_device(debug=ANALYZER_DEBUG_MODE)

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
        self.antenna_offset_btn = TwoParamInput("x offset:", "y offset:")
        self.antenna_offset_btn.set_default((0, 52))
        self.pass_heigth_measurement_radius_btn = TwoParamInput("pass height:", "measurement radius:")
        self.pass_heigth_measurement_radius_btn.set_default((4, 5))

        self._left_wing.addWidget(self.antenna_offset_btn)
        self._left_wing.addWidget(self.pass_heigth_measurement_radius_btn)

        self._left_wing.addWidget(self.path_generation_position)
        self._left_wing.addWidget(self.path_generation_size)

        self.recalculate_path = RecalculatePath()
        self.recalculate_path.pressed.connect(self.update_path)
        self._left_wing.addWidget(self.recalculate_path)

        self.save_data_btn = SavaData()
        self.save_data_btn.pressed.connect(self.save_data)
        self._left_wing.addWidget(self.save_data_btn)

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

        print(f"path_generation_position: {self.path_generation_position.get_vals()}")
        print(f"path_generation_size: {self.path_generation_size.get_vals()}")

        print(f"pass_height_measurement_radius_btn: {self.pass_heigth_measurement_radius_btn.get_vals()}")
        print(f"antenna_offset_btn: {self.antenna_offset_btn.get_vals()}")

        path_x = np.min((self.printer.x_size,
                         self.path_generation_position.get_vals()[0] + self.path_generation_size.get_vals()[0] -
                         self.antenna_offset[0]))

        path_y = np.min((self.printer.y_size,
                         self.path_generation_position.get_vals()[1] + self.path_generation_size.get_vals()[1] -
                         self.antenna_offset[1]))

        printer_size = (path_x, path_y, self.printer.z_size)

        self.antenna_offset = self.antenna_offset_btn.get_vals()
        self.pass_height, self.antenna_measurement_radius = self.pass_heigth_measurement_radius_btn.get_vals()
        self.path, no_bins = simple_pass_3d(
            shift_from_0_0=self.path_generation_position.get_vals(),
            printer_size=printer_size,
            antenna_measurement_radius=self.antenna_measurement_radius,
            antenna_offset=self.antenna_offset,
            pass_height=self.pass_height,
        )

        self.path_plot_canvas.plot_data(
            self.path,
            printer_boundaries=printer_size,
            antenna_offset=self.antenna_offset,
            antenna_measurement_radius=self.antenna_measurement_radius,
        )
        self.path_plot_canvas.draw()

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

    def save_data(self):
        if self.measurement is None:
            print("can not save to file, path is empty")
            return

        measurement = pd.DataFrame(self.measurement)

        fname = QFileDialog.getSaveFileName(
            self,
            "Save data",
            os.getcwd(),
            "CSV File (*.csv);;All Files (*);;Text (*.txt)",
        )
        print(fname)
        measurement.to_csv(fname[0])

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
            self.save_data_btn.enable()
            return

        printer_size = (self.printer.x_size, self.printer.y_size, self.printer.z_size)

        self.update_path()
        if len(self.path) == 0:
            print("could not perform measurement, path did not generate correctly")
            return

        self.printer_head_controller.disable()
        self.recalculate_path.disable()

        self.measurements_plot_canvas.plot_data(self.path, None)

        self.path_plot_canvas.draw()
        self.measurements_plot_canvas.draw()

        print("startup procedure")

        self.thread = threading.Thread(
            target=self.main_loop,
            args=(
                self.path,
                self.printer,
                self.analyzer,
                self.antenna_offset,
                printer_size,
                self.antenna_measurement_radius,
            ),
        )
        self.thread.start()

    def main_loop(
            self,
            path: List[Point],
            printer_handle: Union[MarlinDevice, PrusaDevice, PrinterDeviceMock],
            analyzer_handle: Union[Hameg3010Device, Hameg3010DeviceMock],
            antenna_offset: Tuple[float, float, float],
            printer_size: Tuple[float, float, float],
            antenna_measurement_radius: float,
    ):
        printer_handle.startup_procedure()
        print("Measurement loop ")
        self.measurement: Dict[str, list] = {'x': [],
                                             'y': [],
                                             'z': [],
                                             'm': []}

        max_x = np.max([x for x, _, _ in path])
        max_y = np.max([y for _, y, _ in path])
        min_x = np.min([x for x, _, _ in path])
        min_y = np.min([y for _, y, _ in path])

        print((max_x, max_y, min_x, min_y))

        x_printer_boundaries = (min_x, min_x, max_x, max_x, min_x)
        y_printer_boundaries = (min_y, max_y, max_y, min_y, min_y)

        z = 10

        for x, y in zip(x_printer_boundaries, y_printer_boundaries):
            printer_handle.send_and_await(f"G1 X{x} Y{y} Z{z}")
            print(f"\tx:{x}\ty:{y}\tz:{z}")

        for point in path:
            x, y, z = point

            print("Moving...")
            x = round(x, 3)
            y = round(y, 3)
            z = round(z, 3)
            printer_handle.send_and_await(f"G1 X{x} Y{y} Z{z}")
            print(f"\tx:{x}\ty:{y}\tz:{z}")

            if self.check_for_stop():
                return

            print("Scanning...")
            scan_val = get_level(analyzer_handle, 2.622 * (10 ** 9), 1)

            print(f"\tmeasurement:{scan_val}")

            self.measurement['x'].append(x - antenna_offset[0])
            self.measurement['y'].append(y - antenna_offset[1])
            self.measurement['z'].append(z)
            self.measurement['m'].append(scan_val)

            if self.check_for_stop():
                return

            print("Updating plots...")

            self.path_plot_canvas.plot_data(
                path,
                printer_boundaries=printer_size,
                antenna_offset=antenna_offset,
                antenna_measurement_radius=antenna_measurement_radius,
                highlight=(x, y, z),
            )

            self.measurements_plot_canvas.plot_data(path, self.measurement)

            self.path_plot_canvas.draw()
            self.measurements_plot_canvas.draw()

            if self.check_for_stop():
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
