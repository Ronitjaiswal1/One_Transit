import { useEffect } from 'react'

import { useTwinStore } from '../store/useTwinStore'
import type { SceneId, TwinSnapshot } from '../types/twin'

const WS_BASE = import.meta.env.VITE_TWIN_WS ?? 'ws://127.0.0.1:8000/ws/twin'
const API_BASE = import.meta.env.VITE_TWIN_API ?? 'http://127.0.0.1:8000'

export function useTwinSocket(scene: SceneId): void {
  const setConnected = useTwinStore((s) => s.setConnected)
  const setSnapshot = useTwinStore((s) => s.setSnapshot)

  useEffect(() => {
    let socket: WebSocket | null = null
    let closed = false

    const fetchSnapshot = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/scenes/${scene}`)
        if (!response.ok) return
        const snap = (await response.json()) as TwinSnapshot
        setSnapshot(snap)
      } catch {
        // Connection fallback is handled by websocket retries.
      }
    }

    const connect = () => {
      socket = new WebSocket(`${WS_BASE}?scene=${scene}`)

      socket.onopen = () => {
        setConnected(true)
      }

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as TwinSnapshot
          setSnapshot(payload)
        } catch {
          // Ignore malformed payloads.
        }
      }

      socket.onclose = () => {
        setConnected(false)
        if (!closed) {
          window.setTimeout(connect, 1000)
        }
      }

      socket.onerror = () => {
        socket?.close()
      }
    }

    fetchSnapshot()
    connect()

    return () => {
      closed = true
      socket?.close()
    }
  }, [scene, setConnected, setSnapshot])
}
