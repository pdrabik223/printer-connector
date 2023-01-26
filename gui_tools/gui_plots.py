import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib
from typing import Tuple, List, Optional, Dict

from printer_device_connector.prusa_device import PrusaDevice
from pass_generators.simple_pass import simple_pass_3d

matplotlib.use("Qt5Agg")

Point = Tuple[float, float, float]


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
            printer_boundaries: Tuple[float, float, float],
            antenna_offset: Tuple[float, float],
            antenna_measurement_radius: float,
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

        antenna_x = [pos[0] - antenna_offset[0] for pos in path]
        antenna_y = [pos[1] - antenna_offset[1] for pos in path]

        self.axes2.cla()
        PathPlotCanvas.plot_measurement_areas(
            antenna_x, antenna_y, self.axes2, antenna_measurement_radius
        )
        self.axes2.plot(
            x_printer_boundaries, y_printer_boundaries, color="black", alpha=0.6
        )
        self.axes2.plot(x, y)
        self.axes2.scatter(x, y, color="red")

        if highlight is not None:
            self.axes2.add_patch(
                plt.Circle((highlight[0], highlight[1]), 2, color="black", alpha=1)
            )

        self.axes2.axis("square")
        self.axes2.grid()
        self.axes2.set_xlabel("X [arb. units]")
        self.axes2.set_ylabel("Y [arb. units]")
        self.axes2.set_title("Some thing")

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

    # def highlight(self, point:Point,point_b:P ):

    def show(self):
        self.fig.draw()


class MeasurementsPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=5, dpi=90, min=-22, max=-18):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)
        self.min = min
        self.max = max

        val = []
        for _ in range(10):
            val.append([])
            for _ in range(10):
                val[-1].append((min + max) / 2)

        cp = self.axes.imshow(
            val,
            cmap="seismic",
            vmin=np.min(val),
            vmax=np.max(val),
            interpolation="none",
        )

        self.cbar = self.fig.colorbar(cp, ax=self.axes, extend="both")
        self.cbar.minorticks_on()
        super(MeasurementsPlotCanvas, self).__init__(self.fig)

    def plot_data(
            self,
            path: List[Tuple[float, float, float]],
            measurements: Optional[Dict[str, list]],
    ):
        self.axes.cla()

        no_bins_x = np.unique([x for x, _, _ in path])
        no_bins_y = np.unique([y for _, y, _ in path])

        if measurements is not None:
            values = measurements['m']
        else:
            values = []

        filler = (self.min + self.max) / 2

        val = []
        for _ in no_bins_y:
            val.append([])
            for _ in no_bins_x:
                val[-1].append(filler)

        k: int = 0
        for x in range(len(no_bins_x)):
            for y in range(len(no_bins_y) - 1, -1, -1):
                if k >= len(values):
                    break
                val[y][x] = values[k]
                k += 1

        self.axes.imshow(
            val, cmap="seismic", vmin=self.min, vmax=self.max, interpolation="none"
        )

        self.axes.set_xlabel("X [arb. units]")
        self.axes.set_ylabel("Y [arb. units]")
        self.axes.set_title("Some thing")

    def show(self):
        self.fig.draw()
