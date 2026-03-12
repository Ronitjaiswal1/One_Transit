# Backend (Phase 1 Foundation)

FastAPI service that streams live digital twin scene snapshots to the frontend.

## Run

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start server:

```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health`
- `GET /api/scenes/{scene}` where `scene` is `unified|grid|relay|v2i`
- `WS /ws/twin?scene=unified`

This is the implementation base for the full simulation stack (SimPy + PINN + V2I + V2G).
