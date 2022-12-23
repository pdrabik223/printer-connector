import copy
import math
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt


def simple_pass(
    printer_size: Tuple[float, float, float],
    antenna_offset: Tuple[float, float, float],
    path_width: float,
):
    path = []
    y_direction = 1

    for x in range(0, math.floor((printer_size[0] - antenna_offset[0]) / path_width)):
        for y in range(
            0, math.floor((printer_size[1] - antenna_offset[1]) / path_width)
        ):
            if y_direction == 1:
                path.append(
                    (
                        x * path_width,
                        y * path_width,
                    )
                )
            else:
                path.append(
                    (
                        x * path_width,
                        printer_size[1] - 2 * antenna_offset[1] - y * path_width,
                    )
                )
        y_direction *= -1

    # center on path
    path = [(pos[0] + path_width / 2, pos[1] + path_width / 2) for pos in path]

    # compensate for antenna to extruder offset
    path = [(pos[0] + antenna_offset[0], pos[1] + antenna_offset[1]) for pos in path]
    return path


if __name__ == "__main__":
    #               x    y    z
    printer_size = (220, 220, 200)
    antenna_offset = (5, 10, 0)
    path_width = 5
    antenna_measurement_radius = 30
    pass_height = 120

    path = simple_pass(
        printer_size=printer_size,
        path_width=path_width,
        antenna_offset=antenna_offset,
    )

    path = [(pos[0], pos[1], pass_height) for pos in path]

    x = [pos[0] for pos in path]
    y = [pos[1] for pos in path]
    z = [pos[2] for pos in path]

    x_3d_plot = copy.deepcopy(x)
    y_3d_plot = copy.deepcopy(y)
    z_3d_plot = copy.deepcopy(z)

    x_3d_plot.insert(0, 0)
    y_3d_plot.insert(0, 0)
    z_3d_plot.insert(0, 0)

    ax = plt.figure().add_subplot(projection="3d")
    ax.plot(x_3d_plot, y_3d_plot, z_3d_plot)
    ax.scatter(x_3d_plot, y_3d_plot, z_3d_plot, color="orange", alpha=0.4)
    ax.grid()

    ax = plt.figure().add_subplot()
    ax.plot(x, y)
    ax.scatter(x, y, color="orange", alpha=0.4)
    ax.grid()

    ax = plt.figure().add_subplot()
    # ax.plot(x, y)
    antenna_x = [pos[0] - antenna_offset[0] for pos in path]
    antenna_y = [pos[1] - antenna_offset[1] for pos in path]
    ax.scatter(x, y, color="orange", alpha=0.4)
    ax.scatter(
        antenna_x, antenna_y, color="green", alpha=0.4, s=antenna_measurement_radius
    )
    ax.grid()

    plt.show()
