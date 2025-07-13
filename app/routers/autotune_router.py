from fastapi import APIRouter, HTTPException
from app.schemas.autotune import (
    AutotunePidSimulationDtoRequest,
    AutotunePidDtoRequest,
    AutotunePidDtoResponse,
)
from app.services.autotune_service import sessions
from app.models.session import Session
from app.config import SIM_API

import requests

router = APIRouter()

@router.post("/autotune")
def autotune(req: AutotunePidSimulationDtoRequest):
    sim_payload = {
        "roomId": req.roomId,
        "controllerType": req.controllerType,
        "iterations": req.iterations,
        "timestepSeconds": req.timestepSeconds
    }
    try:
        resp = requests.post(
            f"{SIM_API}/simulations/autotune/cohen-coon",
            json=sim_payload, timeout=5
        )
        resp.raise_for_status()
    except Exception as exc:
        raise HTTPException(502, f"simulator unavailable: {exc}")

    simulation_id = resp.json().get("simulationId")
    if simulation_id is None:
        raise HTTPException(502, "simulator did not return simulationId")

    s = Session(req.roomId, req.iterations)
    sessions[simulation_id] = s
    return {"session_id": simulation_id}

@router.post("/api/power/{simulationId}", response_model=AutotunePidDtoResponse)
def power(simulationId: int, upd: AutotunePidDtoRequest):
    s = sessions.get(simulationId)
    if not s:
        raise HTTPException(404, "session not found")
    if s.done:
        return AutotunePidDtoResponse(outputPower=0.0)

    p = s.relay_power()
    s.append(p, upd.roomTemp)

    if s.finished():
        s.compute_and_store()
        return AutotunePidDtoResponse(outputPower=0.0)
    return AutotunePidDtoResponse(outputPower=p)
