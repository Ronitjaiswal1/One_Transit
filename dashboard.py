from __future__ import annotations

import math
import time
from urllib.parse import quote

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st


st.set_page_config(page_title="Unified DTC Nav-Sync AI", layout="wide")


CYAN = [0, 229, 255, 230]
CYAN_SOFT = [0, 229, 255, 140]
GREEN_DTC = [63, 255, 169, 235]
BLUE_CLUSTER = [72, 163, 255, 235]
RED_ALERT = [255, 78, 100, 240]
YELLOW_WARN = [255, 199, 79, 235]


def inject_theme() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Rajdhani:wght@500;600;700&display=swap');

            :root {
                --base-bg: #101010;
                --panel-bg: rgba(18, 27, 48, 0.78);
                --panel-border: rgba(0, 229, 255, 0.32);
                --accent: #00E5FF;
                --soft-text: #B9D9EF;
            }

            .stApp {
                background:
                    radial-gradient(circle at 12% 20%, rgba(0,229,255,0.12), transparent 34%),
                    radial-gradient(circle at 82% 10%, rgba(88,156,255,0.10), transparent 38%),
                    linear-gradient(140deg, #0b0d16 0%, #11182a 48%, #090d19 100%);
                color: #EAF8FF;
                font-family: 'Rajdhani', sans-serif;
            }

            .main-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 2rem;
                letter-spacing: 0.06em;
                color: #B7ECFF;
                text-transform: uppercase;
                margin-bottom: 0.4rem;
                text-shadow: 0 0 18px rgba(0,229,255,0.35);
            }

            .page-subtitle {
                color: var(--soft-text);
                margin-bottom: 0.9rem;
                font-size: 1.05rem;
            }

            .kpi-card {
                background: var(--panel-bg);
                border: 1px solid var(--panel-border);
                box-shadow: inset 0 0 22px rgba(0, 229, 255, 0.09), 0 0 16px rgba(0, 170, 255, 0.12);
                border-radius: 12px;
                padding: 0.8rem 0.95rem;
                margin-bottom: 0.8rem;
            }

            .kpi-title {
                color: #A5D6F0;
                font-size: 1.1rem;
                margin: 0;
            }

            .kpi-value {
                color: #7BFFCE;
                font-size: 1.8rem;
                line-height: 1.15;
                font-weight: 700;
                margin: 0;
            }

            .alert-value {
                color: #FFC86E;
            }

            .warning-card {
                background: rgba(46, 10, 18, 0.72);
                border: 1px solid rgba(255, 78, 100, 0.45);
                box-shadow: 0 0 22px rgba(255, 78, 100, 0.18);
                border-radius: 12px;
                padding: 0.85rem 0.95rem;
                margin-bottom: 0.65rem;
            }

            .warning-title {
                margin: 0;
                font-family: 'Orbitron', sans-serif;
                color: #FF9AAA;
                font-size: 0.95rem;
            }

            .warning-value {
                margin: 0;
                color: #FFD2D9;
                font-size: 1.2rem;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(10, 20, 37, 0.98), rgba(7, 12, 26, 0.98));
                border-right: 1px solid rgba(0, 229, 255, 0.2);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def records(df: pd.DataFrame) -> list[dict]:
    return df.where(df.notna(), None).to_dict(orient="records")


def deck_chart(layers: list[pdk.Layer], view_state: pdk.ViewState, tooltip_html: str) -> None:
    chart = pdk.Deck(
        map_provider="carto",
        map_style="dark_no_labels",
        initial_view_state=view_state,
        layers=layers,
        tooltip={"html": tooltip_html, "style": {"backgroundColor": "#101726", "color": "#E8F8FF"}},
    )
    st.pydeck_chart(chart, use_container_width=True)


def kpi_panel() -> None:
    st.markdown('<div class="kpi-card"><p class="kpi-title">Fleet Optimization</p><p class="kpi-value">94%</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-card"><p class="kpi-title">Energy Grid Load</p><p class="kpi-value">Stable</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-card"><p class="kpi-title">Active Alerts</p><p class="kpi-value alert-value">2 (Minor)</p></div>', unsafe_allow_html=True)


def bus_icon_url(color_hex: str) -> str:
    svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 90'>
      <defs>
        <filter id='g' x='-60%' y='-60%' width='220%' height='220%'>
          <feGaussianBlur stdDeviation='3' result='b'/>
          <feMerge>
            <feMergeNode in='b'/>
            <feMergeNode in='SourceGraphic'/>
          </feMerge>
        </filter>
      </defs>
      <rect x='18' y='22' rx='9' ry='9' width='124' height='42' fill='none' stroke='{color_hex}' stroke-width='4' filter='url(#g)'/>
      <rect x='32' y='30' width='26' height='12' fill='none' stroke='{color_hex}' stroke-width='2'/>
      <rect x='62' y='30' width='26' height='12' fill='none' stroke='{color_hex}' stroke-width='2'/>
      <rect x='92' y='30' width='26' height='12' fill='none' stroke='{color_hex}' stroke-width='2'/>
      <rect x='122' y='30' width='12' height='24' fill='none' stroke='{color_hex}' stroke-width='2'/>
      <circle cx='48' cy='69' r='8' fill='none' stroke='{color_hex}' stroke-width='3'/>
      <circle cx='110' cy='69' r='8' fill='none' stroke='{color_hex}' stroke-width='3'/>
    </svg>
    """.strip()
    return "data:image/svg+xml;utf8," + quote(svg)


def with_bus_icons(df: pd.DataFrame, color_hex_col: str = "color_hex") -> pd.DataFrame:
    icon_df = df.copy()
    icon_df["icon"] = icon_df[color_hex_col].map(
        lambda color: {
            "url": bus_icon_url(str(color)),
            "width": 160,
            "height": 90,
            "anchorY": 45,
        }
    )
    icon_df["icon_size"] = 7
    return icon_df


def unified_command_page() -> None:
    st.markdown('<div class="main-title">Unified Command Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Map-centric command view of Kashmere Gate ISBT with holographic fleet telemetry and live relay state.</div>',
        unsafe_allow_html=True,
    )

    pulse = 0.45 + 0.55 * (math.sin(time.time() * 2.8) + 1.0) / 2.0
    line_alpha = int(160 + pulse * 90)
    line_width = 8 + pulse * 8

    buses = pd.DataFrame(
        [
            {"bus_id": "DTC-402EV", "lat": 28.6685, "lon": 77.2272, "fleet": "DTC", "battery": 82, "next_relay": "7 mins"},
            {"bus_id": "DTC-155EV", "lat": 28.6672, "lon": 77.2291, "fleet": "DTC", "battery": 80, "next_relay": "11 mins"},
            {"bus_id": "CL-924", "lat": 28.6697, "lon": 77.2234, "fleet": "Cluster", "battery": 76, "next_relay": "9 mins"},
            {"bus_id": "CL-551", "lat": 28.6658, "lon": 77.2259, "fleet": "Cluster", "battery": 84, "next_relay": "12 mins"},
            {"bus_id": "DTC-303E", "lat": 28.6666, "lon": 77.2327, "fleet": "DTC", "battery": 78, "next_relay": "5 mins"},
            {"bus_id": "DTC-101E", "lat": 28.6670, "lon": 77.2337, "fleet": "DTC", "battery": 88, "next_relay": "4 mins"},
        ]
    )
    buses["color"] = buses["fleet"].map({"DTC": GREEN_DTC, "Cluster": BLUE_CLUSTER})
    buses["color_hex"] = buses["fleet"].map({"DTC": "#3fffa9", "Cluster": "#48a3ff"})
    buses["tag"] = (
        "Bus ID: "
        + buses["bus_id"]
        + "\\nBattery: "
        + buses["battery"].astype(str)
        + "%\\nNext Relay: "
        + buses["next_relay"]
    )
    bus_icons = with_bus_icons(buses)

    handover_line = pd.DataFrame(
        [
            {
                "path": [[77.2327, 28.6666], [77.2337, 28.6670]],
                "color": [0, 229, 255, line_alpha],
                "name": "Automated Unlinked Relay Handover in Progress",
                "width": line_width,
            }
        ]
    )
    handover_label = pd.DataFrame(
        [
            {
                "lat": 28.6668,
                "lon": 77.2332,
                "text": "Automated Unlinked Relay\\nHandover in Progress",
                "color": CYAN,
            }
        ]
    )

    columns = st.columns([5.4, 1.55])
    with columns[0]:
        layers = [
            pdk.Layer(
                "ScatterplotLayer",
                records(buses),
                get_position="[lon, lat]",
                get_color="color",
                get_radius=130,
                radius_scale=1.6,
                pickable=True,
            ),
            pdk.Layer(
                "IconLayer",
                records(bus_icons),
                get_icon="icon",
                get_position="[lon, lat]",
                get_size="icon_size",
                size_scale=6,
                pickable=True,
            ),
            pdk.Layer(
                "TextLayer",
                records(buses.assign(lat=buses["lat"] + 0.00045)),
                get_position="[lon, lat]",
                get_text="tag",
                get_color=CYAN,
                get_size=13,
                get_alignment_baseline="'top'",
                get_pixel_offset=[0, -8],
            ),
            pdk.Layer(
                "PathLayer",
                records(handover_line),
                get_path="path",
                get_color="color",
                get_width="width",
                width_min_pixels=3,
                cap_rounded=True,
                pickable=True,
            ),
            pdk.Layer(
                "TextLayer",
                records(handover_label),
                get_position="[lon, lat]",
                get_text="text",
                get_color="color",
                get_size=15,
                get_background=True,
                background_padding=[6, 4],
                get_background_color=[4, 40, 57, 190],
            ),
        ]

        deck_chart(
            layers=layers,
            view_state=pdk.ViewState(latitude=28.6676, longitude=77.2273, zoom=14.6, pitch=57, bearing=16),
            tooltip_html="<b>{bus_id}</b><br/>Fleet: {fleet}<br/>Battery: {battery}%<br/>Next Relay: {next_relay}",
        )

    with columns[1]:
        st.markdown("### Live KPI")
        kpi_panel()


def grid_balancing_page() -> None:
    st.markdown('<div class="main-title">Grid Balancing War Room</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Okhla Depot V2G close-up with peak-shaving red streams, thermal risk scoring, and stabilization telemetry.</div>',
        unsafe_allow_html=True,
    )

    hour = st.sidebar.slider("Peak Shaving Hour", min_value=0, max_value=23, value=16)
    peak_shaving = 15 <= hour <= 19
    pulse = 0.4 + 0.6 * (math.sin(time.time() * 3.4) + 1) / 2

    depot = {"lat": 28.5358, "lon": 77.2726}
    buses = pd.DataFrame(
        [
            {"bus_id": "Bus 03-EV", "lat": 28.5368, "lon": 77.2709, "thermal": 0.91, "v2g_kw": 70},
            {"bus_id": "Bus 12-EV", "lat": 28.5349, "lon": 77.2717, "thermal": 0.68, "v2g_kw": 52},
            {"bus_id": "Bus 19-EV", "lat": 28.5343, "lon": 77.2742, "thermal": 0.88, "v2g_kw": 80},
            {"bus_id": "Bus 28-EV", "lat": 28.5361, "lon": 77.2748, "thermal": 0.74, "v2g_kw": 49},
            {"bus_id": "Bus 34-EV", "lat": 28.5372, "lon": 77.2737, "thermal": 0.94, "v2g_kw": 84},
        ]
    )
    buses["risk"] = np.where(buses["thermal"] >= 0.85, "High Thermal Risk", "Nominal")
    buses["color"] = buses["risk"].map({"High Thermal Risk": RED_ALERT, "Nominal": GREEN_DTC})
    buses["color_hex"] = buses["risk"].map({"High Thermal Risk": "#ff4e64", "Nominal": "#3fffa9"})
    buses["tag"] = (
        buses["bus_id"]
        + "\\n"
        + buses["risk"]
        + "\\nV2G: "
        + buses["v2g_kw"].astype(str)
        + " kW"
    )
    bus_icons = with_bus_icons(buses)

    flows = buses.copy()
    flows["path"] = flows.apply(lambda row: [[row["lon"], row["lat"]], [depot["lon"], depot["lat"]]], axis=1)
    flows["flow_color"] = flows["risk"].map(
        {
            "High Thermal Risk": [255, 65, 82, int(180 + pulse * 65)],
            "Nominal": [255, 119, 119, int(115 + pulse * 55)],
        }
    )
    flows["width"] = np.where(flows["risk"] == "High Thermal Risk", 10 + pulse * 10, 5 + pulse * 4)

    t = np.arange(0, 40)
    base = 92 + 5 * np.sin(t / 4.0)
    demand = base + (25 if peak_shaving else 12) + (np.sin(t / 2.5) * 4)
    v2g = demand - np.where(peak_shaving, 17 + np.sin(t / 3.0) * 3, 7 + np.sin(t / 4.0) * 2)
    graph_df = pd.DataFrame({"Grid Demand": demand, "After V2G": v2g})

    st.markdown(
        '<div class="warning-card"><p class="warning-title">LOCAL GRID DEMAND</p><p class="warning-value">Critical (120% capacity)</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="warning-card"><p class="warning-title">GRID STABILIZING</p><p class="warning-value">V2G Activated</p></div>',
        unsafe_allow_html=True,
    )
    st.line_chart(graph_df, color=["#FF5A74", "#00E5FF"], use_container_width=True)

    layers = [
        pdk.Layer(
            "ColumnLayer",
            [{"lat": depot["lat"], "lon": depot["lon"], "height": 450, "name": "Okhla Depot"}],
            get_position="[lon, lat]",
            get_elevation="height",
            get_fill_color=[43, 61, 92, 220],
            radius=140,
            extruded=True,
            pickable=True,
        ),
        pdk.Layer(
            "IconLayer",
            records(bus_icons),
            get_icon="icon",
            get_position="[lon, lat]",
            get_size="icon_size",
            size_scale=6,
            pickable=True,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            records(buses),
            get_position="[lon, lat]",
            get_color="color",
            get_radius=90,
            pickable=True,
        ),
        pdk.Layer(
            "PathLayer",
            records(flows),
            get_path="path",
            get_color="flow_color",
            get_width="width",
            width_min_pixels=3,
            cap_rounded=True,
            pickable=True,
        ),
        pdk.Layer(
            "TextLayer",
            records(buses.assign(lat=buses["lat"] + 0.00042)),
            get_position="[lon, lat]",
            get_text="tag",
            get_color=[255, 128, 138, 240],
            get_size=14,
            get_background=True,
            get_background_color=[55, 9, 16, 195],
            background_padding=[7, 5],
        ),
        pdk.Layer(
            "TextLayer",
            [{"lat": depot["lat"] + 0.0018, "lon": depot["lon"], "text": "Local Grid Demand: Critical (120% capacity)\\nGrid Stabilizing V2G Activated"}],
            get_position="[lon, lat]",
            get_text="text",
            get_color=[255, 124, 144, 240],
            get_size=16,
            get_background=True,
            get_background_color=[41, 4, 14, 205],
            background_padding=[8, 6],
        ),
    ]

    deck_chart(
        layers=layers,
        view_state=pdk.ViewState(latitude=28.5358, longitude=77.2726, zoom=15.3, pitch=58, bearing=-12),
        tooltip_html="<b>{bus_id}</b><br/>Thermal: {thermal}<br/>Status: {risk}<br/>V2G: {v2g_kw} kW",
    )


def unlinked_relay_page() -> None:
    st.markdown('<div class="main-title">Unlinked Relay Operations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Sarai Kale Khan handover hub with live agent states, relay continuity line, and crew verification telemetry.</div>',
        unsafe_allow_html=True,
    )

    pulse = 0.3 + 0.7 * (math.sin(time.time() * 2.6) + 1) / 2
    relay_width = 8 + pulse * 10

    buses = pd.DataFrame(
        [
            {"bus_id": "DTC-101E", "role": "Arriving Bus", "lat": 28.5886, "lon": 77.2522, "color": RED_ALERT, "color_hex": "#ff4e64"},
            {"bus_id": "DTC-303E", "role": "Departing Bus", "lat": 28.5877, "lon": 77.2541, "color": BLUE_CLUSTER, "color_hex": "#48a3ff"},
            {"bus_id": "DTC-550E", "role": "Standby", "lat": 28.5865, "lon": 77.2518, "color": BLUE_CLUSTER},
        ]
    )
    buses["color_hex"] = buses["color_hex"].fillna("#48a3ff")
    bus_icons = with_bus_icons(buses)

    bus_tags = pd.DataFrame(
        [
            {
                "lat": 28.5892,
                "lon": 77.2523,
                "text": "Arriving Bus (DTC-101E)\\nAgent ID: DTC-101E\\nThermal Health: COOL\\nArrival ETA: On Time",
            },
            {
                "lat": 28.5883,
                "lon": 77.2546,
                "text": "Departing Bus (DTC-303E)\\nReady for relay synchronization",
            },
            {
                "lat": 28.5889,
                "lon": 77.2551,
                "text": "Relay Crew (ID: B32)\\nRest Verified\\nDuty Start: 0 mins",
            },
        ]
    )

    relay_path = pd.DataFrame(
        [
            {
                "path": [[77.2522, 28.5886], [77.2541, 28.5877]],
                "color": [0, 229, 255, int(170 + pulse * 80)],
                "width": relay_width,
                "name": "Automated Unlinked Relay Handover in Progress",
            }
        ]
    )

    cols = st.columns([4.9, 2.05])
    with cols[0]:
        layers = [
            pdk.Layer(
                "IconLayer",
                records(bus_icons),
                get_icon="icon",
                get_position="[lon, lat]",
                get_size="icon_size",
                size_scale=6,
                pickable=True,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                records(buses),
                get_position="[lon, lat]",
                get_color="color",
                get_radius=88,
                pickable=True,
            ),
            pdk.Layer(
                "PathLayer",
                records(relay_path),
                get_path="path",
                get_color="color",
                get_width="width",
                width_min_pixels=3,
                cap_rounded=True,
                pickable=True,
            ),
            pdk.Layer(
                "TextLayer",
                records(bus_tags),
                get_position="[lon, lat]",
                get_text="text",
                get_color=CYAN,
                get_size=14,
                get_background=True,
                get_background_color=[8, 34, 55, 198],
                background_padding=[8, 5],
            ),
        ]
        deck_chart(
            layers=layers,
            view_state=pdk.ViewState(latitude=28.5882, longitude=77.2529, zoom=15.0, pitch=58, bearing=12),
            tooltip_html="<b>{bus_id}</b><br/>Role: {role}",
        )

    with cols[1]:
        st.markdown("### Crew Verification Panel")
        st.markdown('<div class="kpi-card"><p class="kpi-title">Relay Crew</p><p class="kpi-value">ID: B32</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="kpi-card"><p class="kpi-title">Rest Status</p><p class="kpi-value">Verified</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="kpi-card"><p class="kpi-title">Duty Start</p><p class="kpi-value">0 mins</p></div>', unsafe_allow_html=True)
        kpi_panel()


def v2i_greenwave_page() -> None:
    st.markdown('<div class="main-title">V2I Greenwave Priority</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Tilak Marg junction optimization with late-running trigger, signal-level response, and congestion handoff heatmap.</div>',
        unsafe_allow_html=True,
    )

    pulse = 0.35 + 0.65 * (math.sin(time.time() * 3.1) + 1) / 2
    late_alpha = int(155 + pulse * 90)

    late_bus = pd.DataFrame(
        [
            {
                "bus_id": "DTC-43EEV",
                "lat": 28.6213,
                "lon": 77.2337,
                "delay": "Late: 4.5 mins",
                "request": "V2I Handshake Request Active",
                "color": [255, 88, 109, late_alpha],
                "color_hex": "#ff5870",
            }
        ]
    )
    late_bus_icon = with_bus_icons(late_bus)
    signal = pd.DataFrame(
        [
            {
                "node": "Tilak Marg Signal",
                "lat": 28.6221,
                "lon": 77.2354,
                "status": "Green Light Priority Granted (15s Extension)",
                "color": CYAN,
            }
        ]
    )

    chain_points = [
        [77.2337, 28.6213],
        [77.2354, 28.6221],
        [77.2365, 28.6229],
        [77.2374, 28.6216],
    ]
    chain = pd.DataFrame(
        [
            {
                "path": chain_points,
                "color": [0, 229, 255, int(140 + pulse * 90)],
                "width": 8 + pulse * 8,
                "name": "V2I handoff chain",
            }
        ]
    )

    rng = np.random.default_rng(42)
    heat_points = []
    centers = [(28.6218, 77.2349), (28.6209, 77.2367), (28.6228, 77.2339)]
    for center_lat, center_lon in centers:
        for _ in range(120):
            heat_points.append(
                {
                    "lat": center_lat + rng.normal(0, 0.00065),
                    "lon": center_lon + rng.normal(0, 0.00065),
                    "weight": float(1.5 + abs(rng.normal(0, 1.4))),
                }
            )
    heat_df = pd.DataFrame(heat_points)

    tags = pd.DataFrame(
        [
            {
                "lat": 28.62195,
                "lon": 77.2339,
                "text": "Late: 4.5 mins\\nV2I Handshake Request Active",
                "color": [255, 133, 150, 250],
            },
            {
                "lat": 28.6227,
                "lon": 77.2355,
                "text": "Green Light Priority Granted\\n(15s Extension)",
                "color": CYAN,
            },
        ]
    )

    layers = [
        pdk.Layer(
            "HexagonLayer",
            records(heat_df),
            get_position="[lon, lat]",
            get_weight="weight",
            radius=75,
            elevation_scale=45,
            extruded=True,
            coverage=0.85,
            upper_percentile=95,
            color_range=[
                [5, 26, 38],
                [7, 56, 96],
                [0, 120, 194],
                [0, 181, 255],
                [125, 237, 255],
                [220, 250, 255],
            ],
            pickable=True,
        ),
        pdk.Layer(
            "IconLayer",
            records(late_bus_icon),
            get_icon="icon",
            get_position="[lon, lat]",
            get_size="icon_size",
            size_scale=7,
            pickable=True,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            records(late_bus),
            get_position="[lon, lat]",
            get_color="color",
            get_radius=96,
            pickable=True,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            records(signal),
            get_position="[lon, lat]",
            get_color="color",
            get_radius=105,
            pickable=True,
        ),
        pdk.Layer(
            "PathLayer",
            records(chain),
            get_path="path",
            get_color="color",
            get_width="width",
            width_min_pixels=3,
            cap_rounded=True,
            pickable=True,
        ),
        pdk.Layer(
            "TextLayer",
            records(tags),
            get_position="[lon, lat]",
            get_text="text",
            get_color="color",
            get_size=14,
            get_background=True,
            get_background_color=[8, 34, 52, 198],
            background_padding=[8, 6],
        ),
    ]

    deck_chart(
        layers=layers,
        view_state=pdk.ViewState(latitude=28.6218, longitude=77.2349, zoom=15.0, pitch=57, bearing=22),
        tooltip_html="<b>{bus_id}{node}</b><br/>{delay}{status}",
    )


def main() -> None:
    inject_theme()

    st.sidebar.title("DTC Nav-Sync AI")
    page = st.sidebar.radio(
        "War Room Modules",
        [
            "Unified Command",
            "Grid Balancing",
            "Unlinked Relay",
            "V2I Greenwave",
        ],
        index=0,
    )

    st.sidebar.caption("Theme: Deep Dark Mode | Accent: #00E5FF")

    if page == "Unified Command":
        unified_command_page()
    elif page == "Grid Balancing":
        grid_balancing_page()
    elif page == "Unlinked Relay":
        unlinked_relay_page()
    else:
        v2i_greenwave_page()


if __name__ == "__main__":
    main()