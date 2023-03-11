import json
import os
import threading
import time
from copy import copy

from pass_generators.simple_pass import simple_pass_3d_for_gui
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
)
import sys

from gui_tools.gui_buttons import (
    PrinterHeadPositionController,
    StartStopContinueButton,
    TwoParamInput,
    RecalculatePath,
    SaveData,
    ScanTypeBtn,
    ScanType,
    SaveConfig,
    LoadConfig,
    MaskFunction,
    MaskFunctionState,
    LoadData,
    SingleParamInput,
)
from gui_tools.gui_plots import *
from hapmd.src.hameg_ci import set_up_hamed_device

from typing import Union

from printer_device_connector.device_mock import PrinterDeviceMock
from printer_device_connector.marlin_device import MarlinDevice
from printer_device_connector.prusa_device import PrusaDevice
from gui_tools.gui_plots import Point
from hapmd.src.hameg3010.hameg3010device import Hameg3010Device
from hapmd.src.hameg3010.hameg3010device_mock import Hameg3010DeviceMock
from hapmd.src.hameg_ci import get_level
from pocket_vna_main import PocketVnaDevice, PocketVnaDeviceMock

PRINTER_DEBUG_MODE = False
ANALYZER_DEBUG_MODE = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.path = None
        self.antenna_path = None
        self.thread = None
        self.measurement = None
        self.analyzer = None

        self.innit_ui()
        self.printer: Union[MarlinDevice, PrusaDevice, PrinterDeviceMock] = None

        if PRINTER_DEBUG_MODE:
            self.printer: PrinterDeviceMock = PrinterDeviceMock.connect_on_port(
                "COM69 for all I care"
            )
        else:
            self.printer: MarlinDevice = MarlinDevice.connect_on_port("COM5")

    def innit_ui(self):
        self._measurements_plot_canvas = None
        self._path_plot_canvas = None
        self._path_2d_plot_canvas = None

        self.setWindowTitle("MDMA gui")
        self._left_wing = QVBoxLayout()
        self._center_wing = QVBoxLayout()
        self._right_wing = QVBoxLayout()
        self._graphs_layout = QHBoxLayout()
        self._graphs_settings_layout = QHBoxLayout()
        self.printer_head_controller = PrinterHeadPositionController()

        self.printer_head_controller.forward.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.FORWARD)
        )

        self.printer_head_controller.up.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.UP)
        )

        self.printer_head_controller.left.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.LEFT)
        )

        self.printer_head_controller.home.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.HOME)
        )

        self.printer_head_controller.right.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.RIGHT)
        )

        self.printer_head_controller.back.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.BACK)
        )

        self.printer_head_controller.down.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.DOWN)
        )

        self.printer_head_controller.center_extruder.pressed.connect(
            lambda: self.move_extruder(PrinterHeadPositionController.Direction.CENTER)
        )

        self._left_wing.addWidget(self.printer_head_controller)

        self.scan_type_btn = ScanTypeBtn()
        self._left_wing.addWidget(self.scan_type_btn)
        self.add_plots()

        self.path_generation_position = TwoParamInput(
            "sample\nx offset [mm]:", "sample\ny offset [mm]:"
        )

        self.path_generation_size = TwoParamInput("sample\nwidth [mm]:", "sample\nheight [mm]:")

        self.antenna_offset_btn = TwoParamInput(
            "antenna\nx offset [mm]:", "antenna\ny offset [mm]:"
        )

        self.antenna_offset_btn.set_default_from_tuple((0, 52))

        self.pass_heigth_measurement_radius_btn = TwoParamInput(
            "measurement\nheight [mm]:", "measurement\nradius [mm]:"
        )
        self.pass_heigth_measurement_radius_btn.set_default_from_tuple((4, 10))

        self._left_wing.addWidget(self.antenna_offset_btn)
        self._left_wing.addWidget(self.pass_heigth_measurement_radius_btn)

        self._left_wing.addWidget(self.path_generation_position)
        self._left_wing.addWidget(self.path_generation_size)

        self.measure_freq_btn = SingleParamInput("Measurement freq", 1.32)
        self._left_wing.addWidget(self.measure_freq_btn)

        self.recalculate_path = RecalculatePath()
        self.recalculate_path.pressed.connect(self.update_path)
        self.recalculate_path.pressed.connect(self.update_plots)
        self._left_wing.addWidget(self.recalculate_path)

        self.save_data_btn = SaveData()
        self.save_data_btn.pressed.connect(self.save_data)
        self._left_wing.addWidget(self.save_data_btn)

        self.load_data_btn = LoadData()
        self.load_data_btn.pressed.connect(self.load_data)
        self._left_wing.addWidget(self.load_data_btn)

        self.save_config_btn = SaveConfig()
        self.save_config_btn.pressed.connect(self.save_config)
        self._left_wing.addWidget(self.save_config_btn)

        self.load_config_btn = LoadConfig()
        self.load_config_btn.pressed.connect(self.load_config)
        self._left_wing.addWidget(self.load_config_btn)

        self.start_stop_measurement_button = StartStopContinueButton()
        self.start_stop_measurement_button.pressed.connect(self.start_thread)

        self._left_wing.addWidget(self.start_stop_measurement_button)

        self._left_wing.addWidget(self.start_stop_measurement_button)

        self._central_layout = QHBoxLayout()

        self._center_wing.addLayout(self._graphs_settings_layout)
        self._center_wing.addLayout(self._graphs_layout)

        self.logarithmic_radicalization_function = MaskFunction(
            "Logarithmic Radicalization"
        )

        self.logarithmic_radicalization_function.pressed.connect(
            lambda: self.switch_mask_function(
                self.logarithmic_radicalization_function.text()
            )
        )
        self.logarithmic_radicalization_function.pressed.connect(self.update_mask)
        self._right_wing.addWidget(self.logarithmic_radicalization_function)

        self.automatic_cut_off = MaskFunction("Automatic Cut-off")
        self.automatic_cut_off.pressed.connect(
            lambda: self.switch_mask_function(self.automatic_cut_off.text())
        )
        self.automatic_cut_off.pressed.connect(self.update_mask)
        self._right_wing.addWidget(self.automatic_cut_off)

        self._central_layout.addLayout(self._left_wing)
        self._central_layout.addLayout(self._center_wing)
        self._central_layout.addLayout(self._right_wing)

        widget = QWidget()
        widget.setLayout(self._central_layout)
        self.setCentralWidget(widget)

    def update_mask(self):
        if self.measurement is None:
            return
        if not self.check_for_stop():
            return

    def update_path(self):
        print(f"path_generation_position: {self.path_generation_position.get_vals()}")
        print(f"path_generation_size: {self.path_generation_size.get_vals()}")

        print(
            f"pass_height_measurement_radius_btn: {self.pass_heigth_measurement_radius_btn.get_vals()}"
        )
        print(f"antenna_offset_btn: {self.antenna_offset_btn.get_vals()}")

        sample_size = (
            self.path_generation_size.val_a,
            self.path_generation_size.val_b,
            4,
        )

        antenna_offset = self.antenna_offset_btn.get_vals()
        (
            pass_height,
            antenna_measurement_radius,
        ) = self.pass_heigth_measurement_radius_btn.get_vals()

        self.path, self.antenna_path = simple_pass_3d_for_gui(
            sample_shift_from_0_0=self.path_generation_position.get_vals(),
            sample_size=sample_size,
            antenna_measurement_radius=antenna_measurement_radius,
            antenna_offset=antenna_offset,
            pass_height=pass_height,
        )

    def move_extruder(self, direction: PrinterHeadPositionController.Direction):
        print(
            f"moving extruder: {direction}, current position: {self.printer.current_position.to_tuple()}"
        )

        new_position = self.printer.current_position

        if direction == PrinterHeadPositionController.Direction.UP:
            new_position.z += 1

        elif direction == PrinterHeadPositionController.Direction.DOWN:
            new_position.z -= 1

        elif direction == PrinterHeadPositionController.Direction.RIGHT:
            new_position.x += 1

        elif direction == PrinterHeadPositionController.Direction.LEFT:
            new_position.x -= 1

        elif direction == PrinterHeadPositionController.Direction.FORWARD:
            new_position.y += 1

        elif direction == PrinterHeadPositionController.Direction.BACK:
            new_position.y -= 1

        elif direction == PrinterHeadPositionController.Direction.HOME:
            self.printer.send_and_await("G28")
            print(f"new position: {self.printer.current_position.to_tuple()}")
            return

        elif direction == PrinterHeadPositionController.Direction.CENTER:
            if self.printer.current_position.z < 10:
                new_position.z = 10
                self.printer.send_and_await(
                    f"G1 X {self.printer.current_position.x} Y {self.printer.current_position.y} Z {new_position.z}"
                )

            self.printer.send_and_await(
                f"G1 X {self.printer.x_size / 2} Y {self.printer.y_size / 2} Z {new_position.z}"
            )

            print(f"new position: {self.printer.current_position.to_tuple()}")
            return

        self.printer.send_and_await(
            f"G1 X {new_position.x} Y {new_position.y} Z {new_position.z}"
        )

        print(f"new position: {self.printer.current_position.to_tuple()}")

    def save_data(self):
        if self.measurement is None:
            print("can not save to file, path is empty")
            return

        print(self.get_plot_title())
        measurement = pd.DataFrame(self.measurement)

        fname = QFileDialog.getSaveFileName(
            self,
            "Save data",
            os.getcwd(),
            "CSV File (*.csv);;All Files (*);;Text (*.txt)",
        )
        print(fname)
        if fname != "":
            measurement.to_csv(fname[0])

    def load_data(self):
        fname = QFileDialog.getOpenFileName(
            self,
            "Load data",
            os.getcwd(),
            "CSV File (*.csv);;All Files (*);;Text (*.txt)",
        )
        fname = fname[0]
        print(fname)
        if fname == "" or fname is None:
            return

        df = pd.read_csv(fname)
        self.measurement = {"x": df["x"], "y": df["y"], "z": df["z"], "m": df["m"]}
        self.update_path()
        self.update_plots()

    def switch_mask_function(
            self, pressed_button_text: str = "nothing was clicked, all should be grayed out"
    ):
        for i in range(self._right_wing.count()):
            widget: MaskFunction = self._right_wing.itemAt(i).widget()
            if widget.text() != pressed_button_text:
                widget.nadir()
            else:
                if widget.state == MaskFunctionState.OFF:
                    widget.highlight()
                else:
                    widget.nadir()

    def get_config_dict(self):
        return {
            "function": self.scan_type_btn.text(),
            "x_offset": self.antenna_offset_btn.val_a,
            "y_offset": self.antenna_offset_btn.val_b,
            "pass_height": self.pass_heigth_measurement_radius_btn.val_a,
            "measurement_radius": self.pass_heigth_measurement_radius_btn.val_b,
            "x": self.path_generation_position.val_a,
            "y": self.path_generation_position.val_b,
            "width": self.path_generation_size.val_a,
            "height": self.path_generation_size.val_b,
            "measurement_frequency": self.measure_freq_btn.val_a,
        }

    def save_config(self):
        fname = QFileDialog.getSaveFileName(
            self,
            "Save config",
            os.getcwd(),
            "JSON (*.json);;All Files (*);;Text (*.txt)",
        )
        fname = fname[0]
        print(fname)
        if fname != "":
            print(
                f"path_generation_position: {self.path_generation_position.get_vals()}"
            )
            print(f"path_generation_size: {self.path_generation_size.get_vals()}")

            print(
                f"pass_height_measurement_radius_btn: {self.pass_heigth_measurement_radius_btn.get_vals()}"
            )
            print(f"antenna_offset_btn: {self.antenna_offset_btn.get_vals()}")

            data = self.get_config_dict()
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except Exception as ex:
                print("saving failed")
                print(ex)
                pass

    def load_config(self):
        fname = QFileDialog.getOpenFileName(
            self,
            "Load config",
            os.getcwd(),
            "JSON (*.json);;All Files (*);;Text (*.txt)",
        )
        fname = fname[0]
        print(fname)
        if fname != "":
            data = self.get_config_dict()
            try:
                with open(fname) as file:
                    new_data = json.load(file)
                    for param in data.keys():
                        if param in new_data:
                            data[param] = new_data[param]
            except Exception as ex:
                print("loading failed")
                print(ex)
                pass

            self.scan_type_btn.set_state(data["function"])
            self.antenna_offset_btn.set_values(data["x_offset"], data["y_offset"])
            self.antenna_offset_btn.update()
            self.pass_heigth_measurement_radius_btn.set_values(
                data["pass_height"], data["measurement_radius"]
            )
            self.pass_heigth_measurement_radius_btn.update()
            self.path_generation_position.set_values(data["x"], data["y"])
            self.path_generation_position.update()
            self.path_generation_size.set_values(data["width"], data["height"])
            self.measure_freq_btn.set_values(data["measurement_frequency"] / 10 ** 9)
            self.path_generation_size.update()

    def add_plots(self, plot_title: str = None) -> None:
        def helper(plot):
            self._graphs_layout.addWidget(plot)

            toolbar = NavigationToolbar(plot, self)
            self._graphs_settings_layout.addWidget(toolbar)

        self._path_plot_canvas = PathPlotCanvas()
        helper(self._path_plot_canvas)

        self._measurements_plot_canvas = MeasurementsPlotCanvas()
        helper(self._measurements_plot_canvas)

    @property
    def path_plot_canvas(self) -> PathPlotCanvas:
        return self._path_plot_canvas

    @property
    def measurements_plot_canvas(self) -> MeasurementsPlotCanvas:
        return self._measurements_plot_canvas

    def check_for_stop(self):
        return (
                self.start_stop_measurement_button.state
                != StartStopContinueButton.State.STOP
        )

    def close_thread(self):
        self.printer_head_controller.enable()
        self.recalculate_path.enable()

        self.save_data_btn.enable()
        self.load_data_btn.enable()
        self.scan_type_btn.enable()

        self.save_config_btn.enable()
        self.load_config_btn.enable()
        if self.thread is not None:
            self.start_stop_measurement_button.change_state()

    def connect_to_analyzer_device(self):
        if self.analyzer is not None:
            if isinstance(self.analyzer, (PocketVnaDevice, PocketVnaDeviceMock)):
                return

        if self.scan_type_btn.text() in (
                ScanType.ScalarAnalyzer.value,
                ScanType.ScalarAnalyzerBackground.value,
        ):
            self.analyzer = set_up_hamed_device(debug=ANALYZER_DEBUG_MODE)

        elif self.scan_type_btn.text() in (
                ScanType.VectorAnalyzer.value,
                ScanType.VectorAnalyzerBackground.value,
        ):
            if ANALYZER_DEBUG_MODE:
                self.analyzer = PocketVnaDeviceMock()
            else:
                self.analyzer = PocketVnaDevice()

    def get_plot_title(self):
        if self.scan_type_btn.text() in (
                ScanType.ScalarAnalyzer.value,
                ScanType.ScalarAnalyzerBackground.value,
        ):
            cbar_title = 'Return Loss [dB]'

        elif self.scan_type_btn.text() in (
                ScanType.VectorAnalyzer.value,
                ScanType.VectorAnalyzerBackground.value,
        ):
            cbar_title = 'S11 Imag [relative units]'
        else:
            cbar_title = 'none'

        return f"{self.scan_type_btn.text()}, resolution {self.pass_heigth_measurement_radius_btn.val_b} mm, {self.measure_freq_btn.val_a / 10 ** 9}GHz", cbar_title

    def start_thread(self):
        if self.thread is not None:
            print("thread is already running")
            self.thread.join()
            print("thread is closed")
            self.thread = None

        if (
                self.start_stop_measurement_button.state
                == StartStopContinueButton.State.START
        ):
            self.close_thread()
            return

        self.connect_to_analyzer_device()

        self.update_path()
        if len(self.path) == 0:
            print("could not perform measurement, path did not generate correctly")
            return

        self.printer_head_controller.disable()
        self.recalculate_path.disable()
        self.scan_type_btn.disable()
        self.save_data_btn.disable()
        self.load_data_btn.disable()
        self.load_config_btn.disable()
        self.save_config_btn.disable()
        self.measurements_plot_canvas.plot_data(
            self.path,
            self.measurement,
            plot_title=self.get_plot_title()[0],
            color_bar_label=self.get_plot_title()[1]
        )

        self.path_plot_canvas.draw()
        self.measurements_plot_canvas.draw()

        print("startup procedure")

        self.thread = threading.Thread(
            target=self.main_loop,
            args=(),
        )
        self.thread.start()

    def run_outline(self):
        max_x = np.max([x for x, _, _ in self.path])
        max_y = np.max([y for _, y, _ in self.path])
        min_x = np.min([x for x, _, _ in self.path])
        min_y = np.min([y for _, y, _ in self.path])

        print((max_x, max_y, min_x, min_y))

        x_printer_boundaries = (min_x, min_x, max_x, max_x, min_x)
        y_printer_boundaries = (min_y, max_y, max_y, min_y, min_y)

        z = self.pass_heigth_measurement_radius_btn.val_a + 5
        self.printer.speed = 1500

        self.printer.send_and_await(
            f"G1 X{self.printer.current_position.x} Y{self.printer.current_position.y} Z{z}"
        )

        for x, y in zip(x_printer_boundaries, y_printer_boundaries):
            self.printer.send_and_await(f"G1 X{x} Y{y} Z{z}")
            print(f"\tx:{x}\ty:{y}\tz:{z}")

        self.printer.speed = 800

    def perform_scan(self):
        if isinstance(self.analyzer, (PocketVnaDevice, PocketVnaDeviceMock)):
            return self.analyzer.scan(int(self.measure_freq_btn.val_a))

        elif isinstance(self.analyzer, (Hameg3010Device, Hameg3010DeviceMock)):
            scan_val = get_level(self.analyzer, int(self.measure_freq_btn.val_a), 2)

            while scan_val > -17 or scan_val < -22:
                print(f"\tmeasurement:{scan_val}")
                print(f"\trepeating measurement")
                scan_val = get_level(self.analyzer, int(self.measure_freq_btn.val_a), 2)

            return round(scan_val, 4)
        raise Exception("da fuck")

    def update_plots(self, highlight: Optional[Point] = None, draw_all_plots: bool = True):
        antenna_measurement_radius = self.pass_heigth_measurement_radius_btn.val_b

        btn_2_function = {
            "Logarithmic Radicalization": logarithmic_radicalization,
            "Automatic Cut-off": automatic_cut_off,
        }
        if draw_all_plots:
            self.path_plot_canvas.plot_data(
                self.path,
                self.antenna_path,
                antenna_measurement_diameter=antenna_measurement_radius,
                highlight=highlight,
            )
            self.path_plot_canvas.draw()

        if self.measurement is not None:
            for i in range(self._right_wing.count()):
                widget: MaskFunction = self._right_wing.itemAt(i).widget()
                if widget.state == MaskFunctionState.ON:
                    measurement_copy = copy(self.measurement)
                    measurement_copy["m"] = btn_2_function[widget.text()](
                        copy(self.measurement["m"])
                    )
                    self.measurements_plot_canvas.plot_data(
                        self.path,
                        measurement_copy,
                        plot_title=self.get_plot_title()[0],
                        color_bar_label=self.get_plot_title()[1]
                    )
                    break
                if i == self._right_wing.count() - 1:
                    self.measurements_plot_canvas.plot_data(
                        self.path,
                        self.measurement,
                        plot_title=self.get_plot_title()[0],
                        color_bar_label=self.get_plot_title()[1]
                    )

            self.measurements_plot_canvas.draw()

    def main_loop(self):
        if self.scan_type_btn.text() in (
                ScanType.ScalarAnalyzer.value,
                ScanType.VectorAnalyzer.value,
        ):
            self.measurement: Dict[str, list] = {"x": [], "y": [], "z": [], "m": []}
        self.update_plots()
        self.printer.startup_procedure()
        print("Measurement loop ")
        self.run_outline()
        time.sleep(4)

        total_path_length = len([x for x, _, _ in self.path])
        elapsed_time = time.time()

        for id, point in enumerate(self.path):
            start_time = time.time()
            x, y, z = point

            print("Moving...")
            x = round(x, 3)
            y = round(y, 3)
            z = round(z, 3)

            self.printer.send_and_await(f"G1 X{x} Y{y} Z{z}")

            print(f"\tx:{x}\ty:{y}\tz:{z}")

            if self.check_for_stop():
                return

            print("Scanning...")

            scan_val = self.perform_scan()

            print(f"\tmeasurement:{scan_val}")

            if self.scan_type_btn.text() in (
                    ScanType.ScalarAnalyzer.value,
                    ScanType.VectorAnalyzer.value,
            ):
                self.measurement["x"].append(self.antenna_path[id][0])
                self.measurement["y"].append(self.antenna_path[id][1])
                self.measurement["z"].append(self.antenna_path[id][2])
                self.measurement["m"].append(scan_val)

            elif self.scan_type_btn.text() in (
                    ScanType.ScalarAnalyzerBackground.value,
                    ScanType.VectorAnalyzerBackground.value,
            ):
                self.measurement["m"][id] -= scan_val

            else:
                print(f"Scan type: {self.scan_type_btn.state} is not supported")

            if self.check_for_stop():
                return

            print("Updating plots...")

            self.update_plots(highlight=(x, y, z), draw_all_plots=False)

            if self.check_for_stop():
                return

            print(
                f"Time of measurement: {round(time.time() - start_time, 2)}s, "
                f"elapsed time: {round((time.time() - elapsed_time) / 60, 2)}min, "
                f"left time: {int(round(((time.time() - start_time) * (total_path_length - id - 1)) / (60 ** 2), 2))}h "
                f"{int(round(((time.time() - start_time) * (total_path_length - id - 1)) / 60, 2))}min "
                f"{int(round(((time.time() - start_time) * (total_path_length - id - 1)) % 60, 2))}s"
            )

        self.close_thread()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
