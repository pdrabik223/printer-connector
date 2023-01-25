from typing import Tuple, List


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


def simple_pass_3d(
        shift_from_0_0: Tuple[float, float],
        printer_size: Tuple[float, float, float],
        antenna_offset: Tuple[float, float, float],
        antenna_measurement_radius: float,
        pass_height: float,
) -> Tuple[List[Tuple[float, float, float]], Tuple[List[float], List[float]]]:
    # antenna diameter
    antenna_d = antenna_measurement_radius * 2
    x_ps = printer_size[0]
    y_ps = printer_size[1]

    # list of extruder positions when measurement is done``
    # not shifted by antenna offset
    # measurements are spaced by antenna_measurement_radius

    y_measurements_coords = [
        y + shift_from_0_0[1]
        for y in f_range(antenna_measurement_radius, y_ps, antenna_d, include_end=True)
    ]
    x_measurements_coords = [
        x + shift_from_0_0[0]
        for x in f_range(antenna_measurement_radius, x_ps, antenna_d, include_end=True)
    ]

    path = []
    flip = False
    for x in x_measurements_coords:
        for y in y_measurements_coords:
            # if flip:
            #     path.append((x, printer_size[1] - y))
            # else:
            path.append((x, y))

        flip = not flip

    # shift by antenna offset
    path = [(x + antenna_offset[0], y + antenna_offset[1]) for x, y in path]

    # erase all positions that collide with boundaries of printer
    path = [(x, y, pass_height) for x, y in path if x <= x_ps and y <= y_ps]

    return path, (x_measurements_coords, y_measurements_coords)
