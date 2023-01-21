from typing import List, Tuple, Union

from device_connector.device_mock import DeviceMock
from device_connector.marlin_device import MarlinDevice
from device_connector.prusa_device import PrusaDevice
from gui_tools.gui_plots import Point
from hapmd.src.hameg3010.hameg3010device import Hameg3010Device
from hapmd.src.hameg3010.hameg3010device_mock import Hameg3010DeviceMock
from hapmd.src.hameg_ci import get_level

DEBUG_MODE = True


def main_loop(
        window: "MainWindow",
        path: List[Point],
        printer_handle: Union[MarlinDevice, PrusaDevice, DeviceMock],
        hameg_handle: Union[Hameg3010Device, Hameg3010DeviceMock],
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

        if window.check_for_stop():
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

        if window.check_for_stop():
            return

        print("Updating plots...")

        window.path_3d_plot_canvas.plot_data(
            path,
            printer_boundaries=printer_size,
            antenna_offset=antenna_offset,
            antenna_measurement_radius=antenna_measurement_radius,
            highlight=(x, y, z),
        )

        window.measurements_plot_canvas.plot_data(path, measurement)

        window.path_3d_plot_canvas.draw()
        window.measurements_plot_canvas.draw()

        if window.check_for_stop():
            return
