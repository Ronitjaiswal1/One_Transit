import { useMemo } from 'react'

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

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <h2 className="sidebar-title">Unified DTC Nav-Sync AI</h2>
        <p className="sidebar-subtitle">3D Cyber-Physical War Room</p>

        <div className="scene-list">
          {sceneOptions.map((option) => (
            <button
              key={option.id}
              className={`scene-button ${scene === option.id ? 'scene-button-active' : ''}`}
              onClick={() => setScene(option.id)}
            >
              {option.label}
            </button>
          ))}
        </div>

        <div className="conn-box">
          <div className={`conn-dot ${connected ? 'online' : 'offline'}`} />
          <span>{connected ? 'Simulation Stream Connected' : 'Connecting Simulation Stream...'}</span>
        </div>

        <div className="feature-box">
          <h3>Core Controls (Phase 1)</h3>
          <p>Live scene, bus movement, relay beams, and KPI sync.</p>
        </div>

        <div className="feature-box">
          <h3>Next Integrations</h3>
          <p>SimPy + PINN, V2I late-bus logic, V2G peak load-shaving.</p>
        </div>
      </aside>

      <main className="main-view">
        <header className="main-header">
          <div>
            <h1>{activeSnapshot?.title ?? 'Loading War Room...'}</h1>
            <p>{activeSnapshot?.subtitle ?? 'Bootstrapping live digital twin stream.'}</p>
          </div>
          <div className="kpi-panel">
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
          </div>
        </header>

        <section className="scene-area">
          <WarRoomScene buses={activeSnapshot?.buses ?? []} beams={activeSnapshot?.beams ?? []} />
          <div className="tag-layer">
            {(activeSnapshot?.buses ?? []).slice(0, 3).map((bus) => (
              <div key={bus.id} className="floating-tag" style={{ left: `${bus.x}%`, top: `${Math.max(6, bus.y - 12)}%` }}>
                <strong>{bus.id}</strong>
                <span>Battery: {Math.round(bus.battery)}%</span>
                <span>Next Relay: {bus.nextRelayMinutes} mins</span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
