# One_Transit

One_Transit is a Delhi Transport Corporation digital twin prototype built around a live dashboard for fleet operations, relay handovers, depot energy balancing, and V2I signal priority scenarios.

The current app runs as a Streamlit dashboard and renders a live animated command-center scene in code. It is designed around four war-room views inspired by the DTC April 2026 fleet-merger concept:

- Unified Command
- Grid Balancing
- Unlinked Relay
- V2I Greenwave

## Features

- Live dashboard rendering with animated buses and operational overlays
- Neon war-room visual style for cyber-physical monitoring
- Unified command view for fleet movement and relay operations
- Grid balancing scenario with V2G energy-flow highlights
- Unlinked relay handover scenario for crew and vehicle continuity
- V2I signal-priority scenario for congestion management
- GTFS source files included in the repository for route and stop context

## Project Structure

- [dashboard.py](d:\One_Transit\dashboard.py): Main Streamlit app and live dashboard renderer
- [digital_twin.py](d:\One_Transit\digital_twin.py): Basic digital bus model
- [engine.py](d:\One_Transit\engine.py): Supporting simulation logic
- [optimizer.py](d:\One_Transit\optimizer.py): Optimization-related logic
- [preprocess.py](d:\One_Transit\preprocess.py): Data preparation utilities
- [twin_core.py](d:\One_Transit\twin_core.py): GTFS loading and helper functions
- [visualize.py](d:\One_Transit\visualize.py): Visualization support logic
- [img_dtc](d:\One_Transit\img_dtc): Concept-art assets used during dashboard design work
- GTFS data files:
  - [agency.txt](d:\One_Transit\agency.txt)
  - [calendar.txt](d:\One_Transit\calendar.txt)
  - [routes.txt](d:\One_Transit\routes.txt)
  - [shapes.txt](d:\One_Transit\shapes.txt)
  - [stops.txt](d:\One_Transit\stops.txt)
  - [stop_times.txt](d:\One_Transit\stop_times.txt)
  - [trips.txt](d:\One_Transit\trips.txt)

## Requirements

Minimum Python version:

- Python 3.10+

Python packages used by the current app:

- streamlit
- pandas
- numpy
- pydeck

Install them with:

```bash
pip install streamlit pandas numpy pydeck
```

## Run The Dashboard

From the repository root:

```bash
streamlit run dashboard.py
```

By default, Streamlit serves the app at:

```text
http://localhost:8501
```

## Dashboard Views

### 1. Unified Command

The main operational landing page. This view focuses on a central fleet scene with:

- animated bus movement
- live relay beams
- floating operational tags
- KPI stack for optimization, grid load, and active alerts

### 2. Grid Balancing

This page models an Okhla Depot stress scenario with:

- V2G discharge visuals
- red alert buses
- depot stabilization overlays
- demand-critical warning state

### 3. Unlinked Relay

This page focuses on Sarai Kale Khan relay operations with:

- arriving and departing bus coordination
- crew verification state
- handover beam visualization
- live status tags

### 4. V2I Greenwave

This page models a delayed-vehicle priority scenario with:

- a late-running bus
- active V2I handshake signal
- traffic-signal grant indicator
- operational warning overlays

## Notes

- The dashboard is currently implemented as a live Streamlit scene using HTML, CSS, and JavaScript rendered inside the app.
- The GTFS files are present in the repository and can support future integration with real route-driven simulation.
- The visual direction is based on a high-fidelity digital war-room concept and can be further upgraded to a dedicated 3D front-end stack if required.

## Future Direction

If exact cinematic parity with concept-art renders is required, the next step would be to move the front end to a scene-first stack such as React with Three.js or React Three Fiber while keeping Python for data and simulation services.