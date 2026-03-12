import { Canvas } from '@react-three/fiber'
import { Line } from '@react-three/drei'
import { useMemo } from 'react'

import type { BeamState, BusState } from '../types/twin'

const toWorld = (xPct: number, yPct: number): [number, number, number] => {
  const x = (xPct - 50) / 4
  const z = (yPct - 50) / 4
  return [x, 0.3, z]
}

function BusMesh({ bus }: { bus: BusState }) {
  const [x, y, z] = toWorld(bus.x, bus.y)

  const color =
    bus.fleet === 'dtc'
      ? '#3fffa9'
      : bus.fleet === 'cluster'
      ? '#48a3ff'
      : bus.fleet === 'risk'
      ? '#ff5b74'
      : '#ffd05a'

  return (
    <group position={[x, y, z]} rotation={[0, (-bus.angle * Math.PI) / 180, 0]}>
      <mesh>
        <boxGeometry args={[1.4, 0.35, 0.5]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} transparent opacity={0.95} />
      </mesh>
      <mesh position={[0, -0.22, 0.18]}>
        <cylinderGeometry args={[0.1, 0.1, 0.12, 20]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
      </mesh>
      <mesh position={[0, -0.22, -0.18]}>
        <cylinderGeometry args={[0.1, 0.1, 0.12, 20]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
      </mesh>
    </group>
  )
}

function BeamMesh({ beam, buses }: { beam: BeamState; buses: BusState[] }) {
  const byId = useMemo(() => new Map(buses.map((bus) => [bus.id, bus])), [buses])
  const from = byId.get(beam.fromId)
  const to = byId.get(beam.toId)

  if (!from || !to) return null

  const start = toWorld(from.x, from.y)
  const end = toWorld(to.x, to.y)

  return <Line points={[start, end]} color={beam.color} lineWidth={2.6} transparent opacity={0.9} />
}

export function WarRoomScene({ buses, beams }: { buses: BusState[]; beams: BeamState[] }) {
  return (
    <div className="scene-shell">
      <Canvas camera={{ position: [0, 14, 16], fov: 44 }}>
        <color attach="background" args={['#0a1322']} />
        <ambientLight intensity={0.75} />
        <pointLight position={[8, 12, 8]} intensity={1.2} color="#00e5ff" />
        <pointLight position={[-8, 8, -8]} intensity={0.9} color="#48a3ff" />

        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
          <planeGeometry args={[26, 26]} />
          <meshStandardMaterial color="#0f1f37" emissive="#0c1a31" emissiveIntensity={0.35} />
        </mesh>

        <Line points={[[-12, 0.02, -8], [10, 0.02, 8]]} color="#4da3d6" lineWidth={1.2} />
        <Line points={[[-12, 0.02, -1], [12, 0.02, -2]]} color="#4da3d6" lineWidth={1.2} />
        <Line points={[[-8, 0.02, 12], [7, 0.02, -11]]} color="#4da3d6" lineWidth={1.2} />

        {buses.map((bus) => (
          <BusMesh key={bus.id} bus={bus} />
        ))}

        {beams.map((beam) => (
          <BeamMesh key={beam.id} beam={beam} buses={buses} />
        ))}
      </Canvas>
    </div>
  )
}
