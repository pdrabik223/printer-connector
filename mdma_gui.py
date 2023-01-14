import threading
from time import sleep
from random import random

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
    QDialog
)
import sys
from gui_plots.gui_plots import *
from hapmd.src.hameg_ci import set_up_hamed_device, get_level


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

            toolbar = NavigationToolbar(plot, self)
            self._graphs_settings_layout.addWidget(toolbar)

        self._path_3d_plot_canvas = Path3DPlotCanvas()
        helper(self._path_3d_plot_canvas)

        self._path_2d_plot_canvas = Path2DPlotCanvas()
        helper(self._path_2d_plot_canvas)

        self._measurements_plot_canvas = MeasurementsPlotCanvas()
        helper(self._measurements_plot_canvas)

    @property
    def path_3d_plot_canvas(self) -> Path3DPlotCanvas:
        return self._path_3d_plot_canvas

    @property
    def path_2d_plot_canvas(self) -> Path2DPlotCanvas:
        return self._path_2d_plot_canvas

    @property
    def measurements_plot_canvas(self) -> MeasurementsPlotCanvas:
        return self._measurements_plot_canvas

    START_MEASUREMENT = "START"
    STOP_MEASUREMENT = "STOP"

    def check_for_stop(self):
        return self.start_stop_measurement_button.text() == self.START_MEASUREMENT

    def change_text(self):
        if self.start_stop_measurement_button.text() == self.START_MEASUREMENT:
            self.start_stop_measurement_button.setStyleSheet("background-color: rgb(255, 0, 0);")
            self.start_stop_measurement_button.setText(self.STOP_MEASUREMENT)

        elif self.start_stop_measurement_button.text() == self.STOP_MEASUREMENT:
            self.start_stop_measurement_button.setStyleSheet("background-color: rgb(0, 255, 0);")
            self.start_stop_measurement_button.setText(self.START_MEASUREMENT)
        else:

            raise Exception(f"Bad start_stop_measurement_button text: {self.start_stop_measurement_button.text()}")

    def add_start_button(self):
        self.start_stop_measurement_button = QPushButton()

        self.start_stop_measurement_button.setText(self.START_MEASUREMENT)
        self.start_stop_measurement_button.setStyleSheet("background-color: rgb(0, 255, 0);")

        self.start_stop_measurement_button.clicked.connect(self.change_text)
        self.start_stop_measurement_button.clicked.connect(self.start_thread)
        self._left_wing.insertWidget(len(self._left_wing) - 1, self.start_stop_measurement_button)

    def start_thread(self):
        printer_size = (80, 80, 80)
        antenna_offset = (5, 52, 0)
        antenna_measurement_radius = 2
        pass_height = 4

        path, no_bins = simple_pass_3d(
            printer_size=printer_size,
            antenna_measurement_radius=antenna_measurement_radius,
            antenna_offset=antenna_offset,
            pass_height=pass_height
        )

        self.path_3d_plot_canvas.plot_data(path)
        self.path_2d_plot_canvas.plot_data(path,
                                           printer_boundaries=printer_size,
                                           antenna_offset=antenna_offset,
                                           antenna_measurement_radius=antenna_measurement_radius)

        # no_bins_x = no_bins[0]
        # no_bins_y = no_bins[1]
        self.measurements_plot_canvas.plot_data(path, measurements=[], printer_boundaries=printer_size,
                                                no_bins=no_bins)

        self.path_3d_plot_canvas.draw()
        self.path_2d_plot_canvas.draw()
        self.measurements_plot_canvas.draw()

        printer: MarlinDevice = MarlinDevice.connect_on_port("COM5")
        hameg = set_up_hamed_device()
        print("startup procedure")

        thread = threading.Thread(
            target=self.main_loop,
            args=(path, printer, hameg, antenna_offset, printer_size, antenna_measurement_radius, no_bins),
        )
        thread.start()

    def main_loop(self, path: List[Point], printer: MarlinDevice, hameg, antenna_offset: Tuple[float, float, float],
                  printer_size: Tuple[float, float, float],
                  antenna_measurement_radius: float, no_bins
                  ):

        printer.startup_procedure()
        print("Measurement loop ")
        measurement = []
        no_bins_x = len(path)
        no_bins_y = len(path)

        for point in path:
            print("\tMOVE")
            x, y, z = point
            x = round(x, 2)
            y = round(y, 2)
            z = round(z, 2)
            printer.send_and_await(f"G1 X{x} Y{y} Z{z}")
            sleep(1)
            if self.check_for_stop():
                return

            print("\tSCAN")
            scan_val = get_level(hameg, 2.622 * (10 ** 9), 1)
            measurement.append((x - antenna_offset[0], y - antenna_offset[1], z - antenna_offset[2], scan_val))

            if self.check_for_stop():
                return
            print("\tUPDATE PLOTS")

            self.path_3d_plot_canvas.plot_data(path, highlight=(x, y, z))
            self.path_2d_plot_canvas.plot_data(path,
                                               printer_boundaries=printer_size,
                                               antenna_offset=antenna_offset,
                                               antenna_measurement_radius=antenna_measurement_radius,
                                               highlight=(x, y, z))

            self.measurements_plot_canvas.plot_data(path, measurement, printer_boundaries=printer_size,
                                                    no_bins=no_bins)

            self.path_3d_plot_canvas.draw()
            self.path_2d_plot_canvas.draw()
            self.measurements_plot_canvas.draw()
            if self.check_for_stop():
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    #
    # window.path_3d_plot_canvas.plot_data(path)
    # window.path_2d_plot_canvas.plot_data(path, printer_boundaries=printer_size, antenna_offset=antenna_offset,
    #                                      antenna_measurement_radius=antenna_measurement_radius)
    # measurement = [(x - antenna_offset[0], y - antenna_offset[1], z - antenna_offset[2], random()) for x, y, z in
    #                path]
    # window.measurements_plot_canvas.plot_data(measurement, printer_boundaries=printer_size)

    window.show()
    app.exec()
