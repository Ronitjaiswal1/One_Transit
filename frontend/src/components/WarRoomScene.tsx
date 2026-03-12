import { Html, Line, OrbitControls } from '@react-three/drei'
import { Canvas, useFrame } from '@react-three/fiber'
import { useMemo, useRef, useState } from 'react'
import type { Mesh } from 'three'

import type { BeamState, BusState } from '../types/twin'

const toWorld = (xPct: number, yPct: number): [number, number, number] => {
  const x = (xPct - 50) / 3.3
  const z = (yPct - 50) / 3.3
  return [x, 0.3, z]
}

function CityLayer() {
  const blocks = [
    [-9.5, 0.8, -6.5, 2.6, 1.6, 1.8],
    [-5.8, 0.8, -4.6, 1.8, 1.6, 1.4],
    [8.2, 0.8, -5.2, 3.4, 1.6, 2.2],
    [10.5, 0.8, 4.4, 2.2, 1.6, 2.6],
    [5.1, 0.8, 7.7, 3.1, 1.6, 2.4],
    [-8.6, 0.8, 8.1, 2.2, 1.6, 2.3],
  ]

  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <planeGeometry args={[34, 34]} />
        <meshStandardMaterial color="#081629" emissive="#081729" emissiveIntensity={0.6} roughness={0.85} metalness={0.1} />
      </mesh>

      <gridHelper args={[34, 70, '#1f79b0', '#10385e']} position={[0, 0.02, 0]} />

      {blocks.map((item, idx) => (
        <mesh key={idx} position={[item[0], item[1], item[2]]}>
          <boxGeometry args={[item[3], item[4], item[5]]} />
          <meshStandardMaterial color="#0a2743" emissive="#0f3358" emissiveIntensity={0.5} wireframe transparent opacity={0.5} />
        </mesh>
      ))}

      <group position={[7.6, 0.8, -4.1]}>
        <mesh>
          <cylinderGeometry args={[1.9, 1.9, 1.4, 26]} />
          <meshStandardMaterial color="#0d2a45" emissive="#143a62" emissiveIntensity={0.5} wireframe transparent opacity={0.6} />
        </mesh>
      </group>
    </group>
  )
}

function RoadsLayer() {
  return (
    <group>
      <Line points={[[-16, 0.06, 9], [-6, 0.06, 6], [4, 0.06, 2], [13, 0.06, -1], [16, 0.06, -2]]} color="#2a86c2" lineWidth={1.6} transparent opacity={0.55} />
      <Line points={[[-16, 0.08, 8.3], [-6, 0.08, 5.3], [4, 0.08, 1.3], [13, 0.08, -1.8], [16, 0.08, -2.8]]} color="#79d1ff" lineWidth={0.8} transparent opacity={0.45} />

      <Line points={[[-16, 0.06, -2.2], [-8, 0.06, -2.6], [0, 0.06, -2.5], [8, 0.06, -2.9], [16, 0.06, -2.4]]} color="#2a86c2" lineWidth={1.4} transparent opacity={0.55} />
      <Line points={[[-16, 0.08, -3.0], [-8, 0.08, -3.5], [0, 0.08, -3.2], [8, 0.08, -3.5], [16, 0.08, -3.1]]} color="#79d1ff" lineWidth={0.8} transparent opacity={0.45} />

      <Line points={[[-12, 0.06, -13], [-8, 0.06, -9], [-4, 0.06, -5], [0, 0.06, -1], [3.4, 0.06, 3], [6.7, 0.06, 7], [11, 0.06, 12]]} color="#2a86c2" lineWidth={1.5} transparent opacity={0.55} />
      <Line points={[[-12.8, 0.08, -12.3], [-8.9, 0.08, -8.4], [-4.8, 0.08, -4.5], [-1.0, 0.08, -0.8], [2.5, 0.08, 3.2], [5.9, 0.08, 7.4], [10.2, 0.08, 12.7]]} color="#79d1ff" lineWidth={0.8} transparent opacity={0.42} />
    </group>
  )
}

function BusMesh({ bus, selected, onSelect }: { bus: BusState; selected: boolean; onSelect: (bus: BusState) => void }) {
  const [x, y, z] = toWorld(bus.x, bus.y)
  const [hovered, setHovered] = useState(false)
  const bodyRef = useRef<Mesh>(null)

  const color =
    bus.fleet === 'dtc'
      ? '#3fffa9'
      : bus.fleet === 'cluster'
      ? '#48a3ff'
      : bus.fleet === 'risk'
      ? '#ff5b74'
      : '#ffd05a'

  useFrame((_state, delta) => {
    if (!bodyRef.current) return
    const targetScale = selected || hovered ? 1.1 : 1.0
    bodyRef.current.scale.x += (targetScale - bodyRef.current.scale.x) * delta * 8
    bodyRef.current.scale.y += (targetScale - bodyRef.current.scale.y) * delta * 8
    bodyRef.current.scale.z += (targetScale - bodyRef.current.scale.z) * delta * 8
  })

  const isCar = bus.fleet === 'traffic'
  const isSignal = bus.id.toUpperCase().includes('SIGNAL')

  if (isSignal) {
    return (
      <group
        position={[x, y, z]}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        onClick={() => onSelect(bus)}
      >
        <mesh>
          <cylinderGeometry args={[0.08, 0.08, 1.1, 18]} />
          <meshStandardMaterial color="#00e5ff" emissive="#00e5ff" emissiveIntensity={1.0} />
        </mesh>
        <mesh position={[0, 0.35, 0]}>
          <boxGeometry args={[0.26, 0.42, 0.16]} />
          <meshStandardMaterial color="#68f1ff" emissive="#68f1ff" emissiveIntensity={1.1} transparent opacity={0.95} />
        </mesh>
        <mesh position={[0, 0.35, 0.09]}>
          <sphereGeometry args={[0.06, 18, 18]} />
          <meshStandardMaterial color="#00fff2" emissive="#00fff2" emissiveIntensity={1.6} />
        </mesh>
        {(selected || hovered) && (
          <Html distanceFactor={15} position={[0, 1.05, 0]}>
            <div className="bus-chip">{bus.id}</div>
          </Html>
        )}
      </group>
    )
  }

  return (
    <group
      position={[x, y, z]}
      rotation={[0, (-bus.angle * Math.PI) / 180, 0]}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      onClick={() => onSelect(bus)}
    >
      <mesh ref={bodyRef}>
        <boxGeometry args={isCar ? [0.8, 0.22, 0.4] : [1.9, 0.48, 0.72]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.1} transparent opacity={0.95} metalness={0.42} roughness={0.15} />
      </mesh>

      {!isCar && (
        <mesh position={[0.25, 0.02, 0.37]}>
          <boxGeometry args={[1.2, 0.2, 0.03]} />
          <meshStandardMaterial color="#9ce4ff" emissive="#8ee0ff" emissiveIntensity={0.9} transparent opacity={0.75} />
        </mesh>
      )}

      {!isCar && (
        <mesh position={[0.25, 0.02, -0.37]}>
          <boxGeometry args={[1.2, 0.2, 0.03]} />
          <meshStandardMaterial color="#9ce4ff" emissive="#8ee0ff" emissiveIntensity={0.9} transparent opacity={0.75} />
        </mesh>
      )}

      <mesh position={[isCar ? -0.22 : -0.55, -0.26, 0.24]}>
        <cylinderGeometry args={[0.11, 0.11, 0.16, 20]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} />
      </mesh>
      <mesh position={[isCar ? 0.22 : 0.55, -0.26, 0.24]}>
        <cylinderGeometry args={[0.11, 0.11, 0.16, 20]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} />
      </mesh>
      <mesh position={[isCar ? -0.22 : -0.55, -0.26, -0.24]}>
        <cylinderGeometry args={[0.11, 0.11, 0.16, 20]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} />
      </mesh>
      <mesh position={[isCar ? 0.22 : 0.55, -0.26, -0.24]}>
        <cylinderGeometry args={[0.11, 0.11, 0.16, 20]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} />
      </mesh>

      {(selected || hovered) && (
        <Html distanceFactor={15} position={[0, 0.92, 0]}>
          <div className="bus-chip">{bus.id}</div>
        </Html>
      )}
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

  const pulseRef = useRef<Mesh>(null)

  useFrame(({ clock }) => {
    if (!pulseRef.current) return
    const t = (clock.elapsedTime * 0.45) % 1
    pulseRef.current.position.x = start[0] + (end[0] - start[0]) * t
    pulseRef.current.position.y = start[1] + (end[1] - start[1]) * t + 0.02
    pulseRef.current.position.z = start[2] + (end[2] - start[2]) * t
  })

  return (
    <group>
      <Line points={[start, end]} color={beam.color} lineWidth={2.8} transparent opacity={0.95} />
      <Line points={[start, end]} color={beam.color} lineWidth={1.2} transparent opacity={0.6} />
      <mesh ref={pulseRef}>
        <sphereGeometry args={[0.12, 18, 18]} />
        <meshStandardMaterial color={beam.color} emissive={beam.color} emissiveIntensity={1.5} />
      </mesh>
    </group>
  )
}

export function WarRoomScene({
  buses,
  beams,
  onSelectBus,
  selectedBusId,
}: {
  buses: BusState[]
  beams: BeamState[]
  onSelectBus: (bus: BusState) => void
  selectedBusId: string | null
}) {
  return (
    <div className="scene-shell">
      <Canvas camera={{ position: [0, 11.4, 13.2], fov: 48 }}>
        <color attach="background" args={['#081423']} />
        <fog attach="fog" args={['#07111f', 14, 42]} />

        <ambientLight intensity={0.72} />
        <pointLight position={[9, 12, 8]} intensity={1.2} color="#00e5ff" />
        <pointLight position={[-10, 7, -8]} intensity={0.9} color="#4f9cff" />
        <pointLight position={[0, 10, -12]} intensity={0.5} color="#58c3ff" />

        <CityLayer />
        <RoadsLayer />

        {buses.map((bus) => (
          <BusMesh key={bus.id} bus={bus} selected={selectedBusId === bus.id} onSelect={onSelectBus} />
        ))}

        {beams.map((beam) => (
          <BeamMesh key={beam.id} beam={beam} buses={buses} />
        ))}

        <OrbitControls
          enablePan
          enableRotate
          enableZoom
          minDistance={8}
          maxDistance={20}
          maxPolarAngle={Math.PI / 2.15}
          minPolarAngle={Math.PI / 3.4}
          target={[0, 0.25, 0]}
        />
      </Canvas>
    </div>
  )
}
