from typing import List, Optional, Dict
from pydantic import BaseModel

class Sheet(BaseModel):
    number: int
    width: int
    height: int

class ComponentAttribute(BaseModel):
    name: Optional[str] = None
    # Add other possible attributes here

class Component(BaseModel):
    id: str
    type: str
    x: int
    y: int
    rotation: str
    attributes: Dict[str, str] = {}

class Wire(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class Flag(BaseModel):
    x: int
    y: int
    net_name: str

class CircuitData(BaseModel):
    version: str
    sheet: Sheet
    components: List[Component]
    wires: List[Wire]
    flags: List[Flag]

class CircuitRecognitionResponse(BaseModel):
    circuit: CircuitData
    processing_time: float

class ASCConversionResponse(BaseModel):
    version: str
    sheet: Sheet
    components: List[Component]
    wires: List[Wire]
    flags: List[Flag]

class ASCParseResponse(BaseModel):
    version: str
    sheet: Sheet
    components: List[Component]
    wires: List[Wire]
    flags: List[Flag]