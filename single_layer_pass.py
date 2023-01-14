import copy
from typing import List, Tuple
import matplotlib.pyplot as plt

from time import sleep

from device_connector.prusa_device import PrusaDevice
from device_connector.marlin_device import MarlinDevice

from pass_generators.simple_pass import simple_pass, f_range


def plot_measurement_areas(
        x_values: List[float],
        y_values: List[float],
        ax: plt.Axes,
        radius: float,
        color: str = "blue",
        alpha: float = 0.4,
) -> None:
    for x, y in zip(x_values, y_values):
        ax.add_patch(plt.Circle((x, y), radius, color=color, alpha=alpha))


def create_3d_movement_plot(path: List[Tuple[float, float]], pass_height: float):
    path = [(pos[0], pos[1], pass_height) for pos in path]

    x = [pos[0] for pos in path]
    y = [pos[1] for pos in path]
    z = [pos[2] for pos in path]

    x_3d_plot = copy.deepcopy(x)
    y_3d_plot = copy.deepcopy(y)
    z_3d_plot = copy.deepcopy(z)

    # add_starting_point
    x_3d_plot.insert(0, 0)
    y_3d_plot.insert(0, 0)
    z_3d_plot.insert(0, 0)

    ax = plt.figure().add_subplot(projection="3d")
    ax.plot(x_3d_plot, y_3d_plot, z_3d_plot)
    ax.scatter(x_3d_plot, y_3d_plot, z_3d_plot, color="red")
    ax.axis("square")
    ax.grid()


def create_2d_movement_plot(
        path: List[Tuple[float, float]], printer_boundaries: Tuple[float, float, float]
):
    ax = plt.figure().add_subplot()

    x_printer_boundaries = (0, 0, printer_boundaries[0], printer_boundaries[0], 0)
    y_printer_boundaries = (0, printer_boundaries[1], printer_boundaries[1], 1, 0)
    ax.plot(x_printer_boundaries, y_printer_boundaries, color="black", alpha=0.9)

    x = [pos[0] for pos in path]
    y = [pos[1] for pos in path]

    ax.plot(x, y)
    ax.scatter(x, y, color="red")

    ax.grid()


def create_2d_measurement_placement_plot(
        path: List[Tuple[float, float]], printer_boundaries: Tuple[float, float, float]
):
    ax = plt.figure().add_subplot()

    x_printer_boundaries = (0, 0, printer_boundaries[0], printer_boundaries[0], 0)
    y_printer_boundaries = (0, printer_boundaries[1], printer_boundaries[1], 1, 0)
    ax.plot(x_printer_boundaries, y_printer_boundaries, color="black", alpha=0.9)

    x = [pos[0] for pos in path]
    y = [pos[1] for pos in path]

    antenna_x = [pos[0] - antenna_offset[0] for pos in path]
    antenna_y = [pos[1] - antenna_offset[1] for pos in path]

    plot_measurement_areas(antenna_x, antenna_y, ax, antenna_measurement_radius)
    ax.scatter(x, y, color="red", alpha=1)
    ax.axis("square")
    ax.grid()


if __name__ == "__main__":
    #               x    y    z
    printer_size = (180, 180, 100)
    antenna_offset = (5, 10, 0)
    antenna_measurement_radius = 10
    pass_height = 120

    path = simple_pass(
        printer_size=printer_size,
        antenna_measurement_radius=antenna_measurement_radius,
        antenna_offset=antenna_offset,
    )

    create_3d_movement_plot(path=path, pass_height=pass_height)
    create_2d_movement_plot(path=path, printer_boundaries=printer_size)
    create_2d_measurement_placement_plot(path=path, printer_boundaries=printer_size)
    plt.show()

    # perform_scan = input("commence scan [y/n]")
    # if perform_scan not in ('Y', 'Yes', "YES", 'y', 'yes'):
    #     exit(0)

    printer: MarlinDevice = MarlinDevice.connect_on_port("COM5")
    print("startup procedure")

    printer.startup_procedure()
    print("scanning...")
    printer.send_and_await(f"G1 X{0} Y{0} Z{0}")
    # 2.622 GHz

    for position in path:
        x, y, z = position[0], position[1], pass_height
        # print(f"G1 X{x} Y{y} Z{z}")
        printer.send_and_await(f"G1 X{x} Y{y} Z{z}")
        sleep(10)
