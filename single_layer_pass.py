import copy
from typing import List, Tuple
import matplotlib.pyplot as plt


def f_range(
    start: float = 0,
    end: float = 1,
    step: float = 1,
    include_start=True,
    include_end=False,
):
    range = []

    temp_value = start

    if include_start:
        range.append(temp_value)

    temp_value += step
    while temp_value < end:
        range.append(temp_value)
        temp_value += step

    print(temp_value)

    if include_end:
        range.append(temp_value)

    return range


def simple_pass(
    printer_size: Tuple[float, float, float],
    antenna_offset: Tuple[float, float, float],
    antenna_measurement_radius: float,
) -> List[Tuple[float, float]]:

    # antenna diameter
    antenna_d = antenna_measurement_radius * 2
    x_ps = printer_size[0]
    y_ps = printer_size[1]

    # list of extruder positions when measurement is done``
    # not shifted by antenna offset
    # measurements are spaced by antenna_measurement_radius
    y_measurements_coords = [
        y
        for y in f_range(antenna_measurement_radius, y_ps, antenna_d, include_end=True)
    ]
    x_measurements_coords = [
        x
        for x in f_range(antenna_measurement_radius, x_ps, antenna_d, include_end=True)
    ]

    path = []
    for x in x_measurements_coords:
        for y in y_measurements_coords:
            path.append((x, y))

    # shift by antenna offset
    path = [(x + antenna_offset[0], y + antenna_offset[1]) for x, y in path]

    # erase all positions that collide with boundaries of printer
    path = [(x, y) for x, y in path if x <= x_ps and y <= y_ps]

    return path


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
    printer_size = (230, 230, 200)
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
