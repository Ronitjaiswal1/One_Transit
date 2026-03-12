import { create } from 'zustand'

import type { SceneId, TwinSnapshot } from '../types/twin'

interface TwinStore {
  scene: SceneId
  connected: boolean
  snapshot: TwinSnapshot | null
  setScene: (scene: SceneId) => void
  setConnected: (connected: boolean) => void
  setSnapshot: (snapshot: TwinSnapshot) => void
}

export const useTwinStore = create<TwinStore>((set) => ({
  scene: 'unified',
  connected: false,
  snapshot: null,
  setScene: (scene) => set({ scene }),
  setConnected: (connected) => set({ connected }),
  setSnapshot: (snapshot) => set({ snapshot }),
}))
