from pydantic import StrictInt, StrictStr, StrictFloat, Field, BaseModel
from typing import Union

Numeric = Union[StrictInt, StrictFloat]


class PrinterDeviceConfig:
    
    name:StrictStr = Field(default="Unknown printer")
    
    com_port:StrictStr = Field(...)

    width:Numeric = Field(..., title="Print Space in 'x' axis, in millimeters", description="With 0 point at the left of travel space")
    depth:Numeric = Field(..., title="Print Space in 'y' axis, in millimeters", description="With 0 point at the bottom / front bed edge")
    height:Numeric = Field(..., title="Print Space in 'z' axis, in millimeters", description="With 0 point at the bed level")    
    
    nozzle_diameter:Numeric = Field(..., title="Diameter of the nozzle mounted on extruder, in millimeters")

    class Config:
        allow_mutation = False
    
class PrintConfig:
    name :StrictStr = Field(default="Unknown print")
    
    slicer_vendor:StrictStr =Field(..., title="Name of slicer vendor")
    printer_name:StrictStr =Field(..., title="Name of printer for witch print was sliced")
    
    nozzle_diameter:Numeric = Field(..., title="Diameter of the nozzle for witch gcode was prepared, in millimeters") 
    
    print_time:Numeric = Field(default=10,title="Print time in minutes")
    no_layers:Numeric = Field(default=10)
