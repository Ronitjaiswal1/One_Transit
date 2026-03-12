import { useMemo, useState } from 'react'

import { WarRoomScene } from './components/WarRoomScene'
import { useTwinSocket } from './hooks/useTwinSocket'
import { useTwinStore } from './store/useTwinStore'
import type { SceneId } from './types/twin'
import './App.css'

function App() {
  const scene = useTwinStore((s) => s.scene)
  const connected = useTwinStore((s) => s.connected)
  const snapshot = useTwinStore((s) => s.snapshot)
  const setScene = useTwinStore((s) => s.setScene)
  const [selectedBusId, setSelectedBusId] = useState<string | null>(null)

  useTwinSocket(scene)

  const sceneOptions = useMemo(
    () => [
      { id: 'unified', label: 'Unified Command' },
      { id: 'grid', label: 'Grid Balancing' },
      { id: 'relay', label: 'Unlinked Relay' },
      { id: 'v2i', label: 'V2I Greenwave' },
    ] as Array<{ id: SceneId; label: string }>,
    [],
  )

  const activeSnapshot = snapshot

  const statusLabel = connected ? 'Live Sync' : 'Syncing...'

  const overlayBuses = useMemo(() => {
    if (!activeSnapshot) return []
    const important = ['DTC-402EV', 'DTC-303E', 'DTC-101E', 'Bus-03-EV', 'Bus-19-EV', 'DTC-43EEV']
    const selected = selectedBusId ? activeSnapshot.buses.find((bus) => bus.id === selectedBusId) : null
    const spotlight = selected ?? activeSnapshot.buses.find((bus) => important.includes(bus.id))
    const others = activeSnapshot.buses.filter((bus) => bus.id !== spotlight?.id).slice(0, 3)
    return spotlight ? [spotlight, ...others] : others
  }, [activeSnapshot, selectedBusId])

  return (
    <div className="dash-root">
      <aside className="left-rail">
        <div className="brand-mark">DT</div>
        <button className="rail-btn rail-active">⌂</button>
        <button className="rail-btn">◎</button>
        <button className="rail-btn">◫</button>
        <button className="rail-btn">⚙</button>
      </aside>

      <div className="content-shell">
        <header className="top-bar">
          <div className="top-left">Dashboard</div>
          <div className="location-pill">{activeSnapshot?.title ?? 'Initializing Command Center'}</div>
          <div className="top-right">{statusLabel}</div>
        </header>

        <main className="stage-grid">
          <section className="scene-stack">
            <div className="module-switcher">
              {sceneOptions.map((option) => (
                <button
                  key={option.id}
                  className={`module-btn ${scene === option.id ? 'module-btn-active' : ''}`}
                  onClick={() => {
                    setScene(option.id)
                    setSelectedBusId(null)
                  }}
                >
                  {option.label}
                </button>
              ))}
            </div>

            <div className="scene-area">
              <WarRoomScene
                buses={activeSnapshot?.buses ?? []}
                beams={activeSnapshot?.beams ?? []}
                selectedBusId={selectedBusId}
                onSelectBus={(bus) => setSelectedBusId(bus.id)}
              />

              <div className="tag-layer">
                {overlayBuses.map((bus, idx) => (
                  <div
                    key={bus.id}
                    className={`floating-tag ${selectedBusId === bus.id ? 'floating-tag-selected' : ''}`}
                    style={{ left: `${bus.x}%`, top: `${Math.max(11, bus.y - 11 - idx * 1.2)}%` }}
                    onClick={() => setSelectedBusId(bus.id)}
                  >
                    <strong>{bus.id}</strong>
                    <span>Battery: {Math.round(bus.battery)}%</span>
                    <span>Next Relay: {bus.nextRelayMinutes} mins</span>
                    <span>Delay: {bus.delayMinutes.toFixed(1)} mins</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <aside className="kpi-sidebar">
            <h3>Live KPI</h3>

            <article className="kpi-card">
              <h4>Fleet Optimization</h4>
              <p>{activeSnapshot ? `${activeSnapshot.kpi.fleetOptimization}%` : '--'}</p>
            </article>

            <article className="kpi-card">
              <h4>Energy Grid Load</h4>
              <p>{activeSnapshot?.kpi.gridLoad ?? '--'}</p>
            </article>

            <article className="kpi-card warning">
              <h4>Active Alerts</h4>
              <p>{activeSnapshot?.kpi.activeAlerts ?? '--'}</p>
            </article>

            <div className="conn-box">
              <div className={`conn-dot ${connected ? 'online' : 'offline'}`} />
              <span>{connected ? 'Telemetry: Connected' : 'Telemetry: Reconnecting...'}</span>
            </div>

            <div className="feature-box">
              <h3>Interactive Controls</h3>
              <p>Rotate, zoom, and pan the 3D city. Click any bus to inspect details.</p>
            </div>
          </aside>
        </main>
      </div>
    </div>
  )
}

export default App
