from pydantic import BaseModel, Field

class AutotunePidSimulationDtoRequest(BaseModel):
    roomId: int
    controllerType: str = "AUTOTUNE_PID"
    iterations: int
    timestepSeconds: int
    deltaPc: float = Field(..., alias="deltaPc")
    periodSeconds: int = Field(..., alias="period")

class AutotunePidDtoRequest(BaseModel):
    roomTemp: float

class AutotunePidDtoResponse(BaseModel):
    outputPower: float
