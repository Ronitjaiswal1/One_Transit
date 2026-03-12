from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .models import SceneId, TwinSnapshot
from .simulator import TwinSimulator


app = FastAPI(title='One Transit Digital Twin API', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


SIMULATORS: dict[SceneId, TwinSimulator] = {
    'unified': TwinSimulator('unified'),
    'grid': TwinSimulator('grid'),
    'relay': TwinSimulator('relay'),
    'v2i': TwinSimulator('v2i'),
}


async def stream_snapshots(scene: SceneId) -> AsyncGenerator[TwinSnapshot, None]:
    simulator = SIMULATORS[scene]
    while True:
        yield simulator.snapshot()
        await asyncio.sleep(0.35)


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/api/scenes/{scene}', response_model=TwinSnapshot)
async def get_scene_snapshot(scene: SceneId) -> TwinSnapshot:
    return SIMULATORS[scene].snapshot()


@app.websocket('/ws/twin')
async def ws_twin(websocket: WebSocket, scene: SceneId = 'unified') -> None:
    await websocket.accept()
    try:
        async for snapshot in stream_snapshots(scene):
            await websocket.send_json(snapshot.model_dump())
    except WebSocketDisconnect:
        return
