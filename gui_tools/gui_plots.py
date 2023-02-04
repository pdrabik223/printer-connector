import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib
from typing import Tuple, List, Optional, Dict

from printer_device_connector.prusa_device import PrusaDevice

# from pass_generators.simple_pass import simple_pass_3d

matplotlib.use("Qt5Agg")

Point = Tuple[float, float, float]


# TODO make plots faster with : https://www.geeksforgeeks.org/how-to-update-a-plot-in-matplotlib/


class PathPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=5, dpi=90):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        # self.axes = self.fig.add_subplot(111, projection="3d")
        self.axes2 = self.fig.add_subplot(111)

        self.fig.tight_layout()
        super(PathPlotCanvas, self).__init__(self.fig)

    def plot_data(
            self,
            path: List[Point],
            antenna_path: List[Point],
            antenna_measurement_diameter: float,
            highlight: Optional[Point] = None,
    ):
        max_x = np.max([point[0] for point in path])
        max_y = np.max([point[1] for point in path])
        min_x = np.min([point[0] for point in path])
        min_y = np.min([point[1] for point in path])

        x_printer_boundaries = (min_x, min_x, max_x, max_x, min_x)
        y_printer_boundaries = (min_y, max_y, max_y, min_y, min_y)

        x = [pos[0] for pos in path]
        y = [pos[1] for pos in path]

        antenna_x = [pos[0] for pos in antenna_path]
        antenna_y = [pos[1] for pos in antenna_path]

        self.axes2.cla()

        PathPlotCanvas.plot_measurement_areas(
            antenna_x, antenna_y, self.axes2, antenna_measurement_diameter / 2
        )

        self.axes2.plot(
            x_printer_boundaries, y_printer_boundaries, color="black", alpha=0.6
        )

        self.axes2.plot(x, y)

        self.axes2.scatter(x, y, color="red")

        if highlight is not None:
            self.axes2.add_patch(
                plt.Circle((highlight[0], highlight[1]), 1.5, color="black", alpha=1)
            )

        self.axes2.axis("square")
        self.axes2.grid()
        self.axes2.set_xlabel("X [millimeters]")
        self.axes2.set_ylabel("Y [millimeters]")
        self.axes2.set_title("Extruder path")

    @staticmethod
    def plot_measurement_areas(
            x_values: List[float],
            y_values: List[float],
            ax: plt.Axes,
            radius: float,
            color: str = "orange",
            alpha: float = 0.2,
    ) -> None:
        for x, y in zip(x_values, y_values):
            ax.add_patch(plt.Circle((x, y), radius, color=color, alpha=alpha))

    def highlight(self, point: Point, point_b: Point):
        pass

    def show(self):
        self.fig.draw()


class MeasurementsPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=5, dpi=90, min=-20.5, max=-19):
        self.cp = None
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.tight_layout()
        self.axes = self.fig.add_subplot(111)
        self.min = min
        self.max = max

        val = []
        for _ in range(10):
            val.append([])
            for _ in range(10):
                val[-1].append((min + max) / 2)
        self.cb = None
        super(MeasurementsPlotCanvas, self).__init__(self.fig)

    def plot_data(
            self,
            path: List[Tuple[float, float, float]],
            measurements: Optional[Dict[str, List[Tuple[float, float, float, float]]]],
    ):
        self.axes.cla()

        x_labels = np.unique([x for x, _, _ in path])
        y_labels = np.unique([y for _, y, _ in path])

        filler = (self.min + self.max) / 2

        plot_data: Dict[float, Dict[float, float]] = {}

        for id, val in enumerate(path):
            x = val[0]
            y = val[1]
            z = val[2]
            if measurements is not None and id < len(measurements["m"]):
                m = measurements["m"][id]
            else:
                m = filler

            if x not in plot_data.keys():
                plot_data[x] = {y: m}
            plot_data[x][y] = m

        if measurements is not None and len(measurements) > 0:
            min = np.min(measurements["m"])
            max = np.max(measurements["m"])
        else:
            min = filler
            max = filler

        vec_2d = []

        sorted_x = dict(sorted(plot_data.items()))
        for x in sorted_x:
            vec_2d.append([])
            sorted_y = dict(sorted(plot_data[x].items()))
            for y in sorted_y:
                vec_2d[-1].append(plot_data[x][y])

        vec_2d = np.array(vec_2d).T

        self.cp = self.axes.imshow(
            vec_2d,
            cmap="Wistia",
            vmin=min,
            vmax=max,
            interpolation="none",
            origin="lower",
        )

        if self.cb != None:
            self.cb.remove()

        self.cb = self.fig.colorbar(self.cp, ax=self.axes, extend="both")

        self.axes.set_xticks(np.arange(len(x_labels)), labels=x_labels)
        self.axes.set_yticks(np.arange(len(y_labels)), labels=y_labels)
        self.axes.set_xlabel("X [millimeters]")
        self.axes.set_ylabel("Y [millimeters]")
        self.axes.set_title("Scalar spectrum analyzer readouts\nfor 2.622 Ghz")

        # x_start = 0
        # x_end = len(vec_2d)
        # y_start = 0
        # y_end = len(vec_2d[0])
        #
        # print(f"x_start: {x_start}")
        # print(f"x_end: {x_end}")
        # print(f"y_start: {y_start}")
        # print(f"y_end: {y_end}")
        #
        # size = len(vec_2d[0])
        #
        # if size > 10:
        #     return
        #
        # jump_x = (x_end - x_start) / (2.0 * size)
        # jump_y = (y_end - y_start) / (2.0 * size)
        #
        # x_positions = np.linspace(start=x_start, stop=x_end, num=size, endpoint=False)
        # y_positions = np.linspace(start=y_start, stop=y_end, num=size, endpoint=False)
        #
        # for y_index, y in enumerate(y_positions):
        #     for x_index, x in enumerate(x_positions):
        #         label = vec_2d[y_index][x_index]
        #         text_x = x + jump_x - 0.5
        #         text_y = y + jump_y - 0.5
        #         self.axes.text(
        #             text_x, text_y, label, color="black", ha="center", va="center"
        #         )

    def add_measurement(self, measurement: Tuple[float, float, float, float]):
        if self.cp is not None:
            self.cp.set_ydata
            pass

    def show(self):
        self.fig.draw()
