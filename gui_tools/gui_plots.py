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
            antenna_offset: Tuple[float, float, float],
            antenna_measurement_radius: float,
            highlight: Optional[Point] = None,
    ):
        # x = [pos[0] for pos in path]
        # y = [pos[1] for pos in path]
        # z = [pos[2] for pos in path]
        #
        # self.axes.cla()
        # self.axes.plot(x, y, z)
        # self.axes.scatter(x, y, z, color="red")
        #
        # self.axes.grid()
        # self.axes.set_xlabel("X [arb. units]")
        # self.axes.set_ylabel("Y [arb. units]")
        # self.axes.set_title("Some thing")

        x_printer_boundaries = (0, 0, printer_boundaries[0], printer_boundaries[0], 0)
        y_printer_boundaries = (0, printer_boundaries[1], printer_boundaries[1], 0, 0)

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

    def show(self):
        self.fig.draw()


class MeasurementsPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=5, dpi=90):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)

        self.fig.tight_layout()

        self.cp = None
        self.cbar = self.fig.colorbar(self.cp, ax=self.axes, extend='both')
        self.cbar.minorticks_on()

        super(MeasurementsPlotCanvas, self).__init__(self.fig)

    def plot_data(
            self,
            path: List[Tuple[float, float, float]],
            measurements: List[Tuple[float, float, float, float]],
    ):
        self.axes.cla()
        no_bins_x = np.unique([x for x, _, _ in path])
        no_bins_y = np.unique([y for _, y, _ in path])

        values = [m for _, _, _, m in measurements]
        if len(values) == 0:
            filler = 0
        else:
            filler = np.average(values)

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

        self.cp = self.axes.imshow(val, cmap='RdBu', vmin=np.min(val), vmax=np.max(val),
                                   interpolation='none')

        # self.cbar = self.fig.colorbar(self.cp, ax=self.axes, extend='both')
        # self.cbar.ax = self.axes
        # self.cbar.extend = 'both'
        # self.cbar.mappable = self.cp

        self.axes.set_xlabel("X [arb. units]")
        self.axes.set_ylabel("Y [arb. units]")
        self.axes.set_title("Some thing")


def show(self):
    self.fig.draw()
