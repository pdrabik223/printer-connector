import copy
import math
from typing import List, Tuple
import numpy as np
import matplotlib.pyplot as plt


def simple_pass(
    printer_size: Tuple[float, float, float],
    antenna_offset: Tuple[float, float, float],
    antenna_measurement_radius: float,
) -> List[Tuple[float, float]]:
    path = []
    y_direction = 1

    for x in range(
        0,
        math.floor((printer_size[0] - antenna_offset[0]) / antenna_measurement_radius),
    ):
        for y in range(
            0,
            math.floor(
                (printer_size[1] - antenna_offset[1]) / antenna_measurement_radius
            ),
        ):
            if y_direction == 1:
                path.append(
                    (
                        x * antenna_measurement_radius,
                        y * antenna_measurement_radius,
                    )
                )
            else:
                path.append(
                    (
                        x * antenna_measurement_radius,
                        printer_size[1]
                        - 2 * antenna_offset[1]
                        - y * antenna_measurement_radius,
                    )
                )
        y_direction *= -1

    # center on path
    path = [
        (
            pos[0] + antenna_measurement_radius / 2,
            pos[1] + antenna_measurement_radius / 2,
        )
        for pos in path
    ]

    # compensate for antenna to extruder offset
    path = [(pos[0] + antenna_offset[0], pos[1] + antenna_offset[1]) for pos in path]
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


def create_3d_movement_plot(
    path: List[Tuple[float, float]], pass_height: float
):
    
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

def create_2d_movement_plot(path: List[Tuple[float, float]]):
    x = [pos[0] for pos in path]
    y = [pos[1] for pos in path]

    ax = plt.figure().add_subplot()
    ax.plot(x, y)
    ax.scatter(x, y, color="red")
    ax.grid()
    
def create_2d_measurement_placement_plot(path: List[Tuple[float, float]]):
    x = [pos[0] for pos in path]
    y = [pos[1] for pos in path]
    
    ax = plt.figure().add_subplot()
    
    antenna_x = [pos[0] - antenna_offset[0] for pos in path]
    antenna_y = [pos[1] - antenna_offset[1] for pos in path]

    plot_measurement_areas(antenna_x, antenna_y, ax, antenna_measurement_radius)
    ax.scatter(x, y, color="red", alpha=1)
    ax.axis("square")
    ax.grid()

if __name__ == "__main__":
    #               x    y    z
    printer_size = (211.5, 211.5, 200)
    antenna_offset = (5, 10, 0)
    antenna_measurement_radius = 30
    pass_height = 120

    path = simple_pass(
        printer_size=printer_size,
        antenna_measurement_radius=antenna_measurement_radius,
        antenna_offset=antenna_offset,
    )
    create_3d_movement_plot(path=path, pass_height=pass_height)
    create_2d_movement_plot(path=path)
    create_2d_measurement_placement_plot(path=path)

    plt.show()