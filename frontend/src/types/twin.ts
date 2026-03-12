export type SceneId = 'unified' | 'grid' | 'relay' | 'v2i'

export type FleetKind = 'dtc' | 'cluster' | 'risk' | 'traffic'

export interface BusState {
  id: string
  fleet: FleetKind
  x: number
  y: number
  angle: number
  battery: number
  delayMinutes: number
  nextRelayMinutes: number
  thermalRisk: 'low' | 'medium' | 'high'
}

export interface BeamState {
  id: string
  fromId: string
  toId: string
  mode: 'handover' | 'v2g' | 'v2i'
  color: string
}

export interface KpiState {
  fleetOptimization: number
  gridLoad: 'Stable' | 'Elevated' | 'Critical'
  activeAlerts: number
}

export interface TwinSnapshot {
  scene: SceneId
  timestamp: number
  title: string
  subtitle: string
  buses: BusState[]
  beams: BeamState[]
  kpi: KpiState
}
