import threading
from time import sleep
from random import random

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
from gui_plots.gui_plots import *
from hapmd.src.hameg_ci import set_up_hamed_device, get_level

DEBUG_MODE = True


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._measurements_plot_canvas = None
        self._path_3d_plot_canvas = None
        self._path_2d_plot_canvas = None

        self.setWindowTitle("MDMA gui")
        self._left_wing = QVBoxLayout()
        self._right_wing = QVBoxLayout()
        self._graphs_layout = QHBoxLayout()
        self._graphs_settings_layout = QHBoxLayout()

        self._left_wing.addWidget(PrinterHeadPositionControler())

        self.add_plots()
        self.add_start_button()

        self._central_layout = QHBoxLayout()

        self._right_wing.addLayout(self._graphs_settings_layout)
        self._right_wing.addLayout(self._graphs_layout)

        self._central_layout.addLayout(self._left_wing)
        self._central_layout.addLayout(self._right_wing)

        widget = QWidget()
        widget.setLayout(self._central_layout)
        self.setCentralWidget(widget)

    def add_plots(self) -> None:
        def helper(plot):
            self._graphs_layout.addWidget(plot)

            # toolbar = NavigationToolbar(plot, self)
            # self._graphs_settings_layout.addWidget(toolbar)

        self._path_3d_plot_canvas = PathPlotCanvas()
        helper(self._path_3d_plot_canvas)

        # self._path_2d_plot_canvas = Path2DPlotCanvas()
        # helper(self._path_2d_plot_canvas)

        self._measurements_plot_canvas = MeasurementsPlotCanvas()
        helper(self._measurements_plot_canvas)

    @property
    def path_3d_plot_canvas(self) -> PathPlotCanvas:
        return self._path_3d_plot_canvas

    @property
    def measurements_plot_canvas(self) -> MeasurementsPlotCanvas:
        return self._measurements_plot_canvas

    START_MEASUREMENT = "START"
    STOP_MEASUREMENT = "STOP"

    def check_for_stop(self):

        return self.start_stop_measurement_button.text() == self.START_MEASUREMENT

    def change_text(self):
        if self.start_stop_measurement_button.text() == self.START_MEASUREMENT:
            self.start_stop_measurement_button.setStyleSheet(
                "background-color: rgb(255, 0, 0);"
            )
            self.start_stop_measurement_button.setText(self.STOP_MEASUREMENT)

        elif self.start_stop_measurement_button.text() == self.STOP_MEASUREMENT:
            self.start_stop_measurement_button.setStyleSheet(
                "background-color: rgb(0, 255, 0);"
            )
            self.start_stop_measurement_button.setText(self.START_MEASUREMENT)
        else:

            raise Exception(
                f"Bad start_stop_measurement_button text: {self.start_stop_measurement_button.text()}"
            )

    def add_start_button(self):
        self.start_stop_measurement_button = QPushButton()

        self.start_stop_measurement_button.setText(self.START_MEASUREMENT)
        self.start_stop_measurement_button.setStyleSheet("background-color:   ;")

        self.start_stop_measurement_button.clicked.connect(self.change_text)
        self.start_stop_measurement_button.clicked.connect(self.start_thread)
        self._left_wing.addWidget(self.start_stop_measurement_button)

    def start_thread(self):
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

        self.path_3d_plot_canvas.plot_data(
            path,
            printer_boundaries=printer_size,
            antenna_offset=antenna_offset,
            antenna_measurement_radius=antenna_measurement_radius,
        )

        self.measurements_plot_canvas.plot_data(path, measurements=[])

        self.path_3d_plot_canvas.draw()
        self.measurements_plot_canvas.draw()

        if DEBUG_MODE:
            printer: DeviceMock = DeviceMock.connect_on_port("COM5")
        else:
            printer: MarlinDevice = MarlinDevice.connect_on_port("COM5")

        hameg = set_up_hamed_device(debug=DEBUG_MODE)
        print("startup procedure")

        thread = threading.Thread(
            target=self.main_loop,
            args=(
                path,
                printer,
                hameg,
                antenna_offset,
                printer_size,
                antenna_measurement_radius,
            ),
        )
        thread.start()

    def main_loop(
            self,
            path: List[Point],
            printer_handle: MarlinDevice,
            hameg_handle,
            antenna_offset: Tuple[float, float, float],
            printer_size: Tuple[float, float, float],
            antenna_measurement_radius: float,
    ):

        printer_handle.startup_procedure()
        print("Measurement loop ")
        measurement = []
        for point in path:
            print("Moving...")
            x, y, z = point
            x = round(x, 3)
            y = round(y, 3)
            z = round(z, 3)
            printer_handle.send_and_await(f"G1 X{x} Y{y} Z{z}")
            print(f"\tx:{x}\ty:{y}\tz:{z}")

            if self.check_for_stop():
                return

            print("Scanning...")
            scan_val = get_level(hameg_handle, 2.622 * (10 ** 9), 1, DEBUG_MODE)
            print(f"\tmeasurement:{scan_val}")
            measurement.append(
                (
                    x - antenna_offset[0],
                    y - antenna_offset[1],
                    z - antenna_offset[2],
                    scan_val,
                )
            )

            if self.check_for_stop():
                return
            print("Updating plots...")

            self.path_3d_plot_canvas.plot_data(
                path,
                printer_boundaries=printer_size,
                antenna_offset=antenna_offset,
                antenna_measurement_radius=antenna_measurement_radius,
                highlight=(x, y, z),
            )

            self.measurements_plot_canvas.plot_data(path, measurement)

            self.path_3d_plot_canvas.draw()
            # self.path_2d_plot_canvas.draw()
            self.measurements_plot_canvas.draw()
            if self.check_for_stop():
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
