import json
from typing import List, Optional, Union

from pydantic import BaseModel, StrictInt, StrictFloat, Field, StrictStr, root_validator
from assets.ci_colors import Colors

Numeric = Union[StrictFloat, StrictInt]


class HapmdConfig(BaseModel):

    # hameg device must have specified sweep range
    hameg_vid: StrictInt = Field(default=0x0403)
    hameg_pid: StrictInt = Field(default=0xED72)
    hameg_sweep_time: Numeric = Field(default=0)

    hameg_sweep_min_frequency: Numeric = Field(default=1_000_000)
    hameg_sweep_max_frequency: Numeric = Field(default=8_000_000)
    hameg_frequency_step: Numeric = Field(default=1_000_000)

    hameg_frequencies: Optional[List[Numeric]] = Field(default=None)

    rotor_com_port: StrictStr = Field(default="COM3")
    rotor_min_angle: Numeric = Field(default=-110)
    rotor_max_angle: Numeric = Field(default=110)
    rotor_angle_step: Numeric = Field(default=0.5)

    config_json_file_path: StrictStr = Field(default=None)

    @staticmethod
    def from_json_config_file(file_path: StrictStr) -> "HapmdConfig":
        with open(file_path) as f:
            data = json.load(f)
        config = HapmdConfig(**data)
        config.config_json_file_path = file_path
        return config

    @root_validator()
    def calculate_measured_frequencies(cls, values):
        if values.get("hameg_frequencies") is not None:
            values["hameg_sweep_min_frequency"] = 0
            values["hameg_sweep_max_frequency"] = 0
            values["hameg_frequency_step"] = 0
            return values

        hameg_sweep_min_frequency = values.get("hameg_sweep_min_frequency")
        hameg_sweep_max_frequency = values.get("hameg_sweep_max_frequency")
        hameg_frequency_step = values.get("hameg_frequency_step")

        hameg_frequencies = [
            freq
            for freq in range(
                hameg_sweep_min_frequency,
                hameg_sweep_max_frequency,
                hameg_frequency_step,
            )
        ]

        values["hameg_frequencies"] = hameg_frequencies

        return values

    def print_config(self: "HapmdConfig"):
        print(
            f"""
Connecting Hameg Device on VID: {Colors.BOLD}{hex(self.hameg_vid)}{Colors.ENDC} 
Connecting Hameg Device on PID: {Colors.BOLD}{hex(self.hameg_pid)}{Colors.ENDC}
Sweep Time: {Colors.BOLD}{self.hameg_sweep_time}{Colors.ENDC} s"""
        )

        print(
            f"""
Frequency Step: {Colors.BOLD}{self.hameg_frequency_step}{Colors.ENDC} Hz"""
        )
        print(
            f"""
Sweep Start Frequency: {Colors.BOLD}{'{:.3e}'.format(self.hameg_sweep_min_frequency)}{Colors.ENDC} Hz 
Sweep Stop Frequency: {Colors.BOLD}{'{:.3e}'.format(self.hameg_sweep_max_frequency)}{Colors.ENDC} Hz"""
        )

        if self.hameg_frequencies is not None:

            print(f"List of measured frequencies:")
            for f in self.hameg_frequencies:
                print(
                    "\t\t\t\t"
                    + Colors.BOLD
                    + "{:.3e}".format(f)
                    + Colors.ENDC
                    + "Hz"
                    + Colors.ENDC
                )

        print(
            f"""
Connecting Rotor Device on Com port: {Colors.BOLD}{self.rotor_com_port}{Colors.ENDC}
Rotor Step Angle: {Colors.BOLD}{self.rotor_angle_step}{Colors.ENDC}
Rotor Start Angle: {Colors.BOLD}{self.rotor_min_angle}{Colors.ENDC}          
Stop Angle: {Colors.BOLD}{self.rotor_min_angle}{Colors.ENDC}
"""
        )
