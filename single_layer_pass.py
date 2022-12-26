import copy
import math
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt


def simple_pass(
    printer_size: Tuple[float, float, float],
    antenna_offset: Tuple[float, float, float],
    antenna_measurement_radius: float,
):
    path = []
    y_direction = 1

    for x in range(0, math.floor((printer_size[0] - antenna_offset[0]) / antenna_measurement_radius)):
        for y in range(
            0, math.floor((printer_size[1] - antenna_offset[1]) / antenna_measurement_radius)
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
                        printer_size[1] - 2 * antenna_offset[1] - y * antenna_measurement_radius,
                    )
                )
        y_direction *= -1

    # center on path
    path = [(pos[0] + antenna_measurement_radius / 2, pos[1] + antenna_measurement_radius / 2) for pos in path]

    # compensate for antenna to extruder offset
    path = [(pos[0] + antenna_offset[0], pos[1] + antenna_offset[1]) for pos in path]
    return path


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
        antenna_x, antenna_y, color="green", alpha=0.4, s=antenna_measurement_radius**2
    )
    ax.grid()

    ax = plt.figure().add_subplot()
    # ax.plot(x, y)
    
    antenna_x = [0,20,0,20,10]
    antenna_y = [0,20,20,2,10]
    
    dot_size = [1,1,1,1,10**4]
    dot_alpha = [0,0,0,0,0]
    
    # 1.55 for 10
    
    # 1.75 for 8


    ax.scatter(
        antenna_x, antenna_y, color="green", alpha=dot_alpha, s=dot_size     
    )
    ax.add_patch( plt.Circle((10,10),10,color = 'red', alpha=0.4))
    ax.axis('square')
    ax.grid()


    plt.show()
