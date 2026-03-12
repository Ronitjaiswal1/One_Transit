from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Unified DTC Nav-Sync AI", layout="wide")


def page_shell() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Rajdhani:wght@500;600;700&display=swap');
            .stApp {
                background:
                    radial-gradient(circle at 10% 16%, rgba(0, 229, 255, 0.14), transparent 34%),
                    radial-gradient(circle at 83% 10%, rgba(86, 158, 255, 0.12), transparent 35%),
                    linear-gradient(145deg, #070c18 0%, #0f1a2d 52%, #080c17 100%);
                color: #eaf8ff;
                font-family: 'Rajdhani', sans-serif;
            }
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(8, 16, 29, 0.98), rgba(5, 10, 20, 0.98));
                border-right: 1px solid rgba(0, 229, 255, 0.24);
            }
            .title {
                font-family: 'Orbitron', sans-serif;
                color: #bdf0ff;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                text-shadow: 0 0 14px rgba(0, 229, 255, 0.32);
                margin: 0;
            }
            .subtitle {
                margin: 0.2rem 0 0.7rem;
                color: #b7d9ef;
                font-size: 1.05rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def scene_config(page: str) -> dict:
    common = {
        "kpi": [
            {"title": "Fleet Optimization", "value": "94%", "valueClass": "ok"},
            {"title": "Energy Grid Load", "value": "Stable", "valueClass": "ok"},
            {"title": "Active Alerts", "value": "2 (Minor)", "valueClass": "warn"},
        ]
    }

    if page == "Unified Command":
        return {
            **common,
            "header": "Kashmere Gate ISBT",
            "landmark": "Kashmere Gate",
            "buses": [
                {"id": "DTC-402EV", "fleet": "dtc", "x": 21, "y": 30, "angle": -18, "speed": 0.014, "path": [[20, 30], [28, 34], [37, 39], [44, 43]]},
                {"id": "DTC-303E", "fleet": "dtc", "x": 57, "y": 51, "angle": 20, "speed": 0.01, "path": [[56, 51], [62, 48], [70, 45]]},
                {"id": "CL-924", "fleet": "cluster", "x": 12, "y": 42, "angle": -16, "speed": 0.012, "path": [[10, 42], [18, 38], [27, 35]]},
                {"id": "CL-551", "fleet": "cluster", "x": 74, "y": 63, "angle": 12, "speed": 0.009, "path": [[71, 62], [66, 58], [59, 55]]},
                {"id": "DTC-101E", "fleet": "dtc", "x": 67, "y": 45, "angle": 18, "speed": 0.0, "path": [[67, 45], [67, 45]]},
                {"id": "DTC-155EV", "fleet": "cluster", "x": 31, "y": 69, "angle": -26, "speed": 0.008, "path": [[31, 69], [39, 63], [47, 56]]},
            ],
            "tags": [
                {"for": "DTC-402EV", "dx": 2, "dy": -12, "text": "Bus ID: DTC-402EV\\nBattery: 82%\\nNext Relay: 7 mins"},
                {"for": "DTC-101E", "dx": 5, "dy": -11, "text": "Arriving Agent (ID: 504)\\nBattery: 88%\\nETA: On Time"},
                {"for": "DTC-303E", "dx": 7, "dy": -11, "text": "Relay Crew (ID: B32)\\nRest Verified\\nDuty Start: 0 mins"},
            ],
            "beams": [
                {"type": "handover", "from": "DTC-303E", "to": "DTC-101E", "color": "#00E5FF"},
                {"type": "flow", "from": "DTC-402EV", "to": "DTC-303E", "color": "#36ffb1"},
            ],
            "trafficSignal": None,
            "warning": None,
        }

    if page == "Grid Balancing":
        return {
            **common,
            "header": "Okhla Depot, ISBT",
            "landmark": "Okhla Depot",
            "buses": [
                {"id": "Bus 03-EV", "fleet": "red", "x": 22, "y": 56, "angle": 14, "speed": 0.006, "path": [[22, 56], [29, 59], [37, 62]]},
                {"id": "Bus 12-EV", "fleet": "red", "x": 34, "y": 51, "angle": 8, "speed": 0.005, "path": [[34, 51], [41, 54], [48, 58]]},
                {"id": "Bus 19-EV", "fleet": "red", "x": 51, "y": 61, "angle": -12, "speed": 0.007, "path": [[51, 61], [57, 58], [63, 53]]},
                {"id": "Bus 34-EV", "fleet": "red", "x": 63, "y": 67, "angle": 5, "speed": 0.006, "path": [[63, 67], [58, 64], [52, 60]]},
                {"id": "Bus 28-EV", "fleet": "red", "x": 44, "y": 47, "angle": 17, "speed": 0.005, "path": [[44, 47], [49, 50], [55, 54]]},
            ],
            "tags": [
                {"for": "Bus 03-EV", "dx": -3, "dy": -12, "text": "Bus 03-EV: V2G\\nDischarging (70kW)\\nNext Relay: 7 mins"},
                {"for": "Bus 19-EV", "dx": 5, "dy": -12, "text": "Bus 19-EV\\nHigh Thermal Risk\\nV2G: 80kW"},
            ],
            "beams": [
                {"type": "v2g", "from": "Bus 03-EV", "to": "DEPOT", "color": "#ff5168"},
                {"type": "v2g", "from": "Bus 12-EV", "to": "DEPOT", "color": "#ff5168"},
                {"type": "v2g", "from": "Bus 19-EV", "to": "DEPOT", "color": "#ff5168"},
                {"type": "v2g", "from": "Bus 34-EV", "to": "DEPOT", "color": "#ff5168"},
            ],
            "trafficSignal": None,
            "warning": "Local Grid Demand: Critical (120% capacity)\\nGrid Stabilizing V2G Activated",
        }

    if page == "Unlinked Relay":
        return {
            **common,
            "header": "Sarai Kale Khan ISBT",
            "landmark": "Sarai Kale Khan",
            "buses": [
                {"id": "DTC-101E", "fleet": "red", "x": 33, "y": 46, "angle": 15, "speed": 0.003, "path": [[32, 46], [37, 47], [41, 48]]},
                {"id": "DTC-303E", "fleet": "cluster", "x": 57, "y": 43, "angle": 20, "speed": 0.0, "path": [[57, 43], [57, 43]]},
                {"id": "DTC-404E", "fleet": "cluster", "x": 17, "y": 33, "angle": -16, "speed": 0.007, "path": [[17, 33], [24, 36], [31, 40]]},
                {"id": "DTC-540E", "fleet": "cluster", "x": 66, "y": 58, "angle": 13, "speed": 0.006, "path": [[66, 58], [60, 54], [55, 51]]},
            ],
            "tags": [
                {"for": "DTC-101E", "dx": -2, "dy": -13, "text": "Arriving Bus (DTC-101E)\\nAgent ID: DTC-101E\\nThermal Health: COOL\\nArrival ETA: On Time"},
                {"for": "DTC-303E", "dx": 6, "dy": -12, "text": "Relay Crew (ID: B32)\\nRest Verified\\nDuty Start: 0 mins"},
            ],
            "beams": [
                {"type": "handover", "from": "DTC-101E", "to": "DTC-303E", "color": "#00E5FF"},
            ],
            "trafficSignal": None,
            "warning": None,
        }

    return {
        **common,
        "header": "Tilak Marg, Delhi",
        "landmark": "India Gate Axis",
        "buses": [
            {"id": "DTC-43EEV", "fleet": "red", "x": 34, "y": 58, "angle": -13, "speed": 0.01, "path": [[34, 58], [42, 56], [51, 54], [59, 52]]},
            {"id": "CAR-11", "fleet": "car", "x": 17, "y": 33, "angle": -10, "speed": 0.007, "path": [[17, 33], [24, 35], [30, 37]]},
            {"id": "CAR-22", "fleet": "car", "x": 70, "y": 34, "angle": 8, "speed": 0.006, "path": [[70, 34], [64, 36], [57, 38]]},
        ],
        "tags": [
            {"for": "DTC-43EEV", "dx": -3, "dy": -12, "text": "Late: 4.5 mins\\nV2I Handshake Request Active"},
            {"for": "SIGNAL", "dx": 4, "dy": -7, "text": "Green Light Priority Granted\\n(15s Extension)"},
        ],
        "beams": [
            {"type": "v2i", "from": "DTC-43EEV", "to": "SIGNAL", "color": "#00E5FF"},
        ],
        "trafficSignal": {"x": 61, "y": 43},
        "warning": None,
    }


def render_live_scene(config: dict) -> None:
    payload = json.dumps(config)
    html = f"""
    <div id="sceneRoot"></div>
    <script>
      const cfg = {payload};
      const root = document.getElementById('sceneRoot');

      root.innerHTML = `
      <style>
        .scene {{
          position: relative;
          width: 100%;
          height: 78vh;
          min-height: 640px;
          overflow: hidden;
          border-radius: 14px;
          border: 1px solid rgba(0,229,255,0.34);
          background:
            radial-gradient(1200px 520px at 58% 18%, rgba(0, 229, 255, 0.07), transparent 60%),
            linear-gradient(160deg, #061021 0%, #0c1831 40%, #070f21 100%);
          box-shadow: inset 0 0 35px rgba(0,0,0,0.45), 0 0 28px rgba(0,170,255,0.16);
          font-family: 'Rajdhani', sans-serif;
        }}

        .title {{
          position: absolute;
          top: 1.1rem;
          left: 50%;
          transform: translateX(-50%);
          padding: .42rem 1.1rem;
          border: 1px solid rgba(0,229,255,.35);
          border-radius: 10px;
          background: rgba(8,23,42,.75);
          color: #c8f4ff;
          font-family: 'Orbitron', sans-serif;
          letter-spacing: .04em;
          font-size: 1.9rem;
          text-shadow: 0 0 14px rgba(0,229,255,.34);
          z-index: 9;
        }}

        .kpi-wrap {{
          position: absolute;
          right: 1.2%;
          top: 11.5%;
          width: 18%;
          min-width: 210px;
          z-index: 8;
          display: grid;
          gap: .55rem;
        }}

        .kpi {{
          background: rgba(10,28,49,.76);
          border: 1px solid rgba(0,229,255,.34);
          border-radius: 10px;
          padding: .65rem .72rem;
          box-shadow: inset 0 0 14px rgba(0,229,255,.1);
          color: #d8f6ff;
        }}

        .kpi .t {{ font-size: 1.18rem; opacity: .95; }}
        .kpi .v {{ font-size: 2rem; font-weight: 700; color: #7bffce; line-height: 1; }}
        .kpi .v.warn {{ color: #ffc86e; }}

        .grid-bg, .landmark {{ position: absolute; inset: 0; }}

        .road {{
          fill: none;
          stroke: rgba(83, 154, 227, 0.34);
          stroke-width: 10;
          filter: drop-shadow(0 0 7px rgba(0,140,255,.34));
        }}

        .lane {{
          fill: none;
          stroke: rgba(153, 220, 255, 0.26);
          stroke-width: 1.8;
          stroke-dasharray: 9 8;
        }}

        .landmark path, .landmark rect, .landmark circle {{
          fill: none;
          stroke: rgba(139, 208, 255, 0.26);
          stroke-width: 1.5;
        }}

        .bus {{
          position: absolute;
          width: 88px;
          height: 38px;
          transform-origin: center center;
          z-index: 6;
          filter: drop-shadow(0 0 8px currentColor);
        }}

        .bus svg {{ width: 100%; height: 100%; overflow: visible; }}

        .bus.dtc {{ color: #3fffa9; }}
        .bus.cluster {{ color: #48a3ff; }}
        .bus.red {{ color: #ff5b74; }}
        .bus.car {{ color: #ffd45f; width: 44px; height: 22px; }}

        .beam {{
          position: absolute;
          height: 3px;
          transform-origin: 0 50%;
          border-radius: 999px;
          z-index: 5;
          opacity: .95;
          animation: beamPulse 1.3s ease-in-out infinite;
        }}

        .tag {{
          position: absolute;
          white-space: pre-line;
          padding: .35rem .52rem;
          background: rgba(8,34,55,0.7);
          border: 1px solid rgba(0,229,255,.4);
          border-radius: 9px;
          color: #def6ff;
          font-size: 1.1rem;
          line-height: 1.05;
          box-shadow: inset 0 0 12px rgba(0,229,255,.1), 0 0 11px rgba(0,170,255,.12);
          z-index: 7;
        }}

        .warning {{
          position: absolute;
          left: 51%;
          top: 18%;
          white-space: pre-line;
          padding: .5rem .7rem;
          background: rgba(62,9,19,.72);
          border: 1px solid rgba(255,90,114,.58);
          border-radius: 10px;
          color: #ffd5dd;
          font-size: 1.2rem;
          z-index: 8;
          box-shadow: 0 0 14px rgba(255,90,114,.26);
        }}

        .signal {{
          position: absolute;
          width: 22px;
          height: 58px;
          border: 2px solid #00e5ff;
          border-radius: 6px;
          box-shadow: 0 0 12px #00e5ff;
          z-index: 6;
        }}

        .signal:before {{
          content: '';
          position: absolute;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #00e5ff;
          left: 4px;
          top: 8px;
          box-shadow: 0 0 12px #00e5ff;
          animation: signalPulse 1s ease-in-out infinite;
        }}

        @keyframes beamPulse {{
          0% {{ opacity: .5; }}
          50% {{ opacity: 1; }}
          100% {{ opacity: .5; }}
        }}

        @keyframes signalPulse {{
          0% {{ transform: scale(.95); opacity: .7; }}
          50% {{ transform: scale(1.08); opacity: 1; }}
          100% {{ transform: scale(.95); opacity: .7; }}
        }}
      </style>

      <div class="scene">
        <div class="title">${{cfg.header}}</div>

        <svg class="grid-bg" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path class="road" d="M-5,82 C20,72 35,68 58,58 C72,52 90,47 105,40" />
          <path class="road" d="M8,22 C20,28 36,36 46,45 C55,54 64,66 74,78" />
          <path class="road" d="M-5,46 C20,42 35,40 53,42 C72,44 88,46 105,44" />
          <path class="lane" d="M-5,82 C20,72 35,68 58,58 C72,52 90,47 105,40" />
          <path class="lane" d="M8,22 C20,28 36,36 46,45 C55,54 64,66 74,78" />
          <path class="lane" d="M-5,46 C20,42 35,40 53,42 C72,44 88,46 105,44" />
        </svg>

        <svg class="landmark" viewBox="0 0 100 100" preserveAspectRatio="none">
          <rect x="53" y="41" width="22" height="18" rx="1"/>
          <rect x="57" y="45" width="14" height="10" rx="1"/>
          <circle cx="64" cy="33" r="7" />
          <path d="M12,21 L20,15 L28,21 L36,15 L44,21" />
          <path d="M10,24 L46,24" />
          <text x="56" y="38" fill="rgba(154,220,255,.5)" style="font-size:2.7px;">${{cfg.landmark}}</text>
        </svg>

        <div class="kpi-wrap"></div>
      </div>`;

      const scene = root.querySelector('.scene');
      const kpiWrap = root.querySelector('.kpi-wrap');

      cfg.kpi.forEach(card => {{
        const el = document.createElement('div');
        el.className = 'kpi';
        el.innerHTML = `<div class="t">${{card.title}}</div><div class="v ${{card.valueClass}}">${{card.value}}</div>`;
        kpiWrap.appendChild(el);
      }});

      const busElements = new Map();

      function busMarkup(kind) {{
        if (kind === 'car') {{
          return `<svg viewBox="0 0 120 64"><rect x="18" y="18" width="84" height="24" rx="7" fill="none" stroke="currentColor" stroke-width="4"/><circle cx="34" cy="49" r="8" fill="none" stroke="currentColor" stroke-width="4"/><circle cx="86" cy="49" r="8" fill="none" stroke="currentColor" stroke-width="4"/></svg>`;
        }}
        return `<svg viewBox="0 0 220 100"><rect x="16" y="22" width="184" height="52" rx="9" fill="none" stroke="currentColor" stroke-width="5"/><rect x="30" y="30" width="34" height="16" fill="none" stroke="currentColor" stroke-width="3"/><rect x="68" y="30" width="34" height="16" fill="none" stroke="currentColor" stroke-width="3"/><rect x="106" y="30" width="34" height="16" fill="none" stroke="currentColor" stroke-width="3"/><rect x="144" y="30" width="28" height="22" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="52" cy="82" r="12" fill="none" stroke="currentColor" stroke-width="4"/><circle cx="160" cy="82" r="12" fill="none" stroke="currentColor" stroke-width="4"/></svg>`;
      }}

      cfg.buses.forEach(bus => {{
        const busEl = document.createElement('div');
        busEl.className = `bus ${{bus.fleet}}`;
        busEl.style.left = `${{bus.x}}%`;
        busEl.style.top = `${{bus.y}}%`;
        busEl.style.transform = `translate(-50%, -50%) rotate(${{bus.angle}}deg)`;
        busEl.innerHTML = busMarkup(bus.fleet);
        scene.appendChild(busEl);
        busElements.set(bus.id, {{ el: busEl, t: 0, ...bus }});
      }});

      function getPoint(path, t) {{
        if (!path || path.length < 2) return [0, 0, 0];
        const segs = path.length - 1;
        const p = Math.max(0, Math.min(0.9999, t)) * segs;
        const i = Math.floor(p);
        const r = p - i;
        const a = path[i];
        const b = path[i + 1];
        const x = a[0] + (b[0] - a[0]) * r;
        const y = a[1] + (b[1] - a[1]) * r;
        const ang = Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI;
        return [x, y, ang];
      }}

      function posOf(id) {{
        if (id === 'DEPOT') return [62, 48, 0];
        if (id === 'SIGNAL' && cfg.trafficSignal) return [cfg.trafficSignal.x, cfg.trafficSignal.y, 0];
        const obj = busElements.get(id);
        if (!obj) return [50, 50, 0];
        const left = parseFloat(obj.el.style.left);
        const top = parseFloat(obj.el.style.top);
        return [left, top, 0];
      }}

      const beamEls = [];
      cfg.beams.forEach(beam => {{
        const el = document.createElement('div');
        el.className = 'beam';
        el.style.background = `linear-gradient(90deg, rgba(0,0,0,0), ${{beam.color}})`;
        el.style.boxShadow = `0 0 12px ${{beam.color}}`;
        scene.appendChild(el);
        beamEls.push({{ def: beam, el }});
      }});

      if (cfg.trafficSignal) {{
        const sig = document.createElement('div');
        sig.className = 'signal';
        sig.style.left = `${{cfg.trafficSignal.x}}%`;
        sig.style.top = `${{cfg.trafficSignal.y}}%`;
        sig.style.transform = 'translate(-50%, -50%)';
        scene.appendChild(sig);
      }}

      const tagEls = [];
      cfg.tags.forEach(tag => {{
        const el = document.createElement('div');
        el.className = 'tag';
        el.textContent = tag.text;
        scene.appendChild(el);
        tagEls.push({{ def: tag, el }});
      }});

      if (cfg.warning) {{
        const warning = document.createElement('div');
        warning.className = 'warning';
        warning.textContent = cfg.warning;
        scene.appendChild(warning);
      }}

      function updateBeam(beam) {{
        const [x1, y1] = posOf(beam.def.from);
        const [x2, y2] = posOf(beam.def.to);
        const dx = x2 - x1;
        const dy = y2 - y1;
        const len = Math.sqrt(dx*dx + dy*dy);
        const ang = Math.atan2(dy, dx) * 180 / Math.PI;
        beam.el.style.left = `${{x1}}%`;
        beam.el.style.top = `${{y1}}%`;
        beam.el.style.width = `${{len}}%`;
        beam.el.style.transform = `translate(0,-50%) rotate(${{ang}}deg)`;
      }}

      function updateTag(tagObj) {{
        let [x, y] = posOf(tagObj.def.for);
        x += (tagObj.def.dx || 0);
        y += (tagObj.def.dy || 0);
        tagObj.el.style.left = `${{x}}%`;
        tagObj.el.style.top = `${{y}}%`;
        tagObj.el.style.transform = 'translate(-50%, -100%)';
      }}

      function animate() {{
        busElements.forEach(bus => {{
          if (bus.speed > 0 && bus.path && bus.path.length > 1) {{
            bus.t = (bus.t + bus.speed) % 1;
            const [x, y, ang] = getPoint(bus.path, bus.t);
            bus.el.style.left = `${{x}}%`;
            bus.el.style.top = `${{y}}%`;
            bus.el.style.transform = `translate(-50%, -50%) rotate(${{ang}}deg)`;
          }}
        }});

        beamEls.forEach(updateBeam);
        tagEls.forEach(updateTag);
        requestAnimationFrame(animate);
      }}

      animate();
    </script>
    """
    components.html(html, height=760, scrolling=False)


def main() -> None:
    page_shell()
    st.markdown('<h1 class="title">Unified DTC Nav-Sync AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Live cyber-physical digital twin scene with animated buses, relay logic, V2G flows, and V2I signaling.</p>',
        unsafe_allow_html=True,
    )

    st.sidebar.title("War Room Controls")
    page = st.sidebar.radio(
        "View",
        ["Unified Command", "Grid Balancing", "Unlinked Relay", "V2I Greenwave"],
        index=0,
    )

    config = scene_config(page)
    render_live_scene(config)


if __name__ == "__main__":
    main()
