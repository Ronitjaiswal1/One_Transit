from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SceneId = Literal['unified', 'grid', 'relay', 'v2i']
FleetKind = Literal['dtc', 'cluster', 'risk', 'traffic']
ThermalRisk = Literal['low', 'medium', 'high']
BeamMode = Literal['handover', 'v2g', 'v2i']
GridLoad = Literal['Stable', 'Elevated', 'Critical']


class BusState(BaseModel):
    id: str
    fleet: FleetKind
    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)
    angle: float
    battery: float = Field(ge=0, le=100)
    delayMinutes: float
    nextRelayMinutes: int
    thermalRisk: ThermalRisk


class BeamState(BaseModel):
    id: str
    fromId: str
    toId: str
    mode: BeamMode
    color: str


class KpiState(BaseModel):
    fleetOptimization: int
    gridLoad: GridLoad
    activeAlerts: int


class TwinSnapshot(BaseModel):
    scene: SceneId
    timestamp: float
    title: str
    subtitle: str
    buses: list[BusState]
    beams: list[BeamState]
    kpi: KpiState
