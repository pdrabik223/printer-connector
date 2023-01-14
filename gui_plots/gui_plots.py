import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib
from typing import Tuple, List, Optional

from device_connector.prusa_device import PrusaDevice
from pass_generators.simple_pass import simple_pass_3d

matplotlib.use("Qt5Agg")

Point = Tuple[float, float, float]


class Path3DPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=5, dpi=90):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111, projection="3d")

        self.fig.tight_layout()
        super(Path3DPlotCanvas, self).__init__(self.fig)

    def plot_data(self, path: List[Point], highlight: Optional[Point] = None):
        x = [pos[0] for pos in path]
        y = [pos[1] for pos in path]
        z = [pos[2] for pos in path]

        self.axes.cla()
        self.axes.plot(x, y, z)
        self.axes.scatter(x, y, z, color="red")
        # if highlight is not None:
        #     self.axes.add_patch(plt.Circle((highlight[0], highlight[1]), 2, color="violet", alpha=1))

        # self.axes.axis("square")
        self.axes.grid()

        self.axes.set_xlabel("X [arb. units]")
        self.axes.set_ylabel("Y [arb. units]")
        self.axes.set_title("Some thing")

    def show(self):
        self.fig.draw()


class Path2DPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=5, dpi=90):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)

        self.fig.tight_layout()
        super(Path2DPlotCanvas, self).__init__(self.fig)

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

    def plot_data(self, path: List[Point], printer_boundaries: Tuple[float, float, float],
                  antenna_offset: Tuple[float, float, float], antenna_measurement_radius: float,
                  highlight: Optional[Point] = None):
        x_printer_boundaries = (0, 0, printer_boundaries[0], printer_boundaries[0], 0)
        y_printer_boundaries = (0, printer_boundaries[1], printer_boundaries[1], 0, 0)

        x = [pos[0] for pos in path]
        y = [pos[1] for pos in path]

        antenna_x = [pos[0] - antenna_offset[0] for pos in path]
        antenna_y = [pos[1] - antenna_offset[1] for pos in path]

        self.axes.cla()
        Path2DPlotCanvas.plot_measurement_areas(antenna_x, antenna_y, self.axes, antenna_measurement_radius)
        self.axes.plot(x_printer_boundaries, y_printer_boundaries, color="black", alpha=0.6)
        self.axes.plot(x, y)
        self.axes.scatter(x, y, color="red")

        if highlight is not None:
            self.axes.add_patch(plt.Circle((highlight[0], highlight[1]), 2, color="black", alpha=1))

        self.axes.axis("square")
        self.axes.grid()
        self.axes.set_xlabel("X [arb. units]")
        self.axes.set_ylabel("Y [arb. units]")
        self.axes.set_title("Some thing")

    def show(self):
        self.fig.draw()


class MeasurementsPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=5, dpi=90):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)

        self.fig.tight_layout()
        super(MeasurementsPlotCanvas, self).__init__(self.fig)

    def plot_data(self, path: List[Tuple[float, float, float]],
                  measurements: List[Tuple[float, float, float, float]],
                  printer_boundaries: Tuple[float, float, float],
                  no_bins: Tuple[list, list]):

        # x_printer_boundaries = (0, 0, printer_boundaries[0], printer_boundaries[0], 0)
        # y_printer_boundaries = (0, printer_boundaries[1], printer_boundaries[1], 0, 0)
        # self.axes.plot(x_printer_boundaries, y_printer_boundaries, color="black", alpha=0.9)

        val = []
        for _ in no_bins[0]:
            val.append([])
            for _ in no_bins[1]:
                val[-1].append(-19.7)

        len_x = len(no_bins[0])
        len_y = len(no_bins[1])
        for id, measurement in enumerate(measurements):
            _, _, _, m = measurement
            val[id % len_x][int(id / len_x)] = m

        x, y = no_bins[0], no_bins[1]
        x, y = np.meshgrid(no_bins[0], no_bins[1])
        # x = [pos[0] for pos in path]
        # y = [pos[1] for pos in path]

        # val = [(0, 0, 0) for _ in path]

        # print(type(val[0]))

        # cp = self.axes.contour(x, y, vmin=np.min(val), vmax=np.max(val), shading='auto')
        cp = self.axes.imshow(val)
        # self.axes.colorbar(cp)
        self.axes.set_xlabel("X [arb. units]")
        self.axes.set_ylabel("Y [arb. units]")
        self.axes.set_title("Some thing")


def show(self):
    self.fig.draw()
