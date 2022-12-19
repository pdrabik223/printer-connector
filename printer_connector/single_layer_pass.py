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

    for x in range(0, int(printer_size[0] / path_width)):
        for y in range(0, int((printer_size[1] / path_width) - antenna_offset[1])):
            if y_direction == 1:
                path.append(
                    (
                        path_width / 2 + x * path_width + antenna_offset[0],
                        path_width / 2 + y * path_width + antenna_offset[1],
                    )
                )
            else:
                path.append(
                    (
                        path_width / 2 + x * path_width + antenna_offset[0],
                        path_width / 2
                        + printer_size[1]
                        - y * path_width
                        + antenna_offset[1],
                    )
                )
        y_direction *= -1

    return path


if __name__ == "__main__":
    #               x    y    z
    printer_size = (200, 200, 200)
    antenna_offset = (5, 10, 0)
    path_width = 10
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

    ax = plt.figure().add_subplot(projection="3d")
    ax.plot(x, y, z)
    ax.scatter(x, y, z)
    ax.grid()

    axx = plt.figure().add_subplot()
    axx.plot(x, y)
    axx.scatter(x, y)
    axx.grid()

    plt.show()
