from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="Unified DTC Nav-Sync AI", layout="wide")


def inject_theme() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Rajdhani:wght@500;600;700&display=swap');

            :root {
                --bg: #0a0f1c;
                --panel: rgba(12, 28, 49, 0.78);
                --stroke: rgba(0, 229, 255, 0.35);
                --cyan: #00E5FF;
                --green: #7BFFCE;
                --amber: #FFC86E;
            }

            .stApp {
                background:
                    radial-gradient(circle at 10% 15%, rgba(0, 229, 255, 0.13), transparent 32%),
                    radial-gradient(circle at 90% 8%, rgba(108, 170, 255, 0.11), transparent 34%),
                    linear-gradient(145deg, #080c17 0%, #0f1a2e 55%, #090d18 100%);
                color: #E7F7FF;
                font-family: 'Rajdhani', sans-serif;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(7, 16, 30, 0.98), rgba(5, 12, 24, 0.98));
                border-right: 1px solid rgba(0, 229, 255, 0.22);
            }

            .scene-wrap {
                position: relative;
                width: 100%;
                height: 76vh;
                min-height: 620px;
                border: 1px solid rgba(0, 229, 255, 0.35);
                border-radius: 14px;
                overflow: hidden;
                box-shadow: 0 0 35px rgba(0, 213, 255, 0.16), inset 0 0 30px rgba(0, 0, 0, 0.4);
            }

            .scene-bg {
                position: absolute;
                inset: 0;
                background-size: cover;
                background-position: center center;
                filter: contrast(1.08) saturate(1.08);
            }

            .scene-overlay {
                position: absolute;
                inset: 0;
                background:
                    linear-gradient(180deg, rgba(2, 8, 22, 0.24), rgba(1, 7, 19, 0.37)),
                    radial-gradient(circle at 75% 18%, rgba(0, 229, 255, 0.08), transparent 26%);
                pointer-events: none;
            }

            .scene-title {
                position: absolute;
                top: 1.1rem;
                left: 50%;
                transform: translateX(-50%);
                padding: 0.45rem 1.2rem;
                border: 1px solid rgba(0, 229, 255, 0.35);
                border-radius: 10px;
                background: rgba(7, 20, 38, 0.72);
                font-family: 'Orbitron', sans-serif;
                font-size: 1.75rem;
                letter-spacing: 0.05em;
                color: #C8F4FF;
                text-shadow: 0 0 14px rgba(0, 229, 255, 0.34);
            }

            .hud-card {
                position: absolute;
                background: rgba(8, 33, 51, 0.66);
                border: 1px solid rgba(0, 229, 255, 0.4);
                border-radius: 10px;
                box-shadow: inset 0 0 16px rgba(0, 229, 255, 0.12), 0 0 15px rgba(0, 180, 255, 0.12);
                color: #DFF7FF;
                padding: 0.45rem 0.62rem;
                line-height: 1.05;
                font-size: 1.5rem;
                white-space: pre-line;
            }

            .kpi-stack {
                position: absolute;
                top: 12%;
                right: 1.1%;
                width: 17.5%;
                min-width: 215px;
                display: grid;
                gap: 0.55rem;
                z-index: 3;
            }

            .kpi {
                background: var(--panel);
                border: 1px solid var(--stroke);
                border-radius: 11px;
                padding: 0.72rem;
                box-shadow: inset 0 0 18px rgba(0, 229, 255, 0.11);
            }

            .kpi-title {
                margin: 0;
                color: #B7DEEF;
                font-size: 1.3rem;
            }

            .kpi-value {
                margin: 0;
                color: var(--green);
                font-size: 2.1rem;
                font-weight: 700;
            }

            .kpi-value.warn {
                color: var(--amber);
            }

            .bus-glow {
                position: absolute;
                width: 64px;
                height: 24px;
                border-radius: 4px;
                border: 2px solid currentColor;
                box-shadow: 0 0 14px currentColor;
                animation: pulse 1.8s ease-in-out infinite;
                z-index: 2;
            }

            .bus-glow::before,
            .bus-glow::after {
                content: '';
                position: absolute;
                bottom: -8px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: 2px solid currentColor;
            }

            .bus-glow::before { left: 7px; }
            .bus-glow::after { right: 7px; }

            .bus-green { color: #3FFFA9; }
            .bus-blue { color: #48A3FF; }
            .bus-red { color: #FF5B74; }

            .beam {
                position: absolute;
                height: 3px;
                transform-origin: left center;
                border-radius: 999px;
                background: linear-gradient(90deg, rgba(0, 229, 255, 0.2), rgba(0, 229, 255, 0.92));
                box-shadow: 0 0 12px rgba(0, 229, 255, 0.9);
                animation: beam 1.25s ease-in-out infinite;
                z-index: 2;
            }

            .beam.red {
                background: linear-gradient(90deg, rgba(255, 90, 114, 0.25), rgba(255, 90, 114, 0.98));
                box-shadow: 0 0 14px rgba(255, 90, 114, 0.95);
            }

            @keyframes pulse {
                0% { opacity: 0.68; transform: scale(1.0); }
                50% { opacity: 1.0; transform: scale(1.04); }
                100% { opacity: 0.68; transform: scale(1.0); }
            }

            @keyframes beam {
                0% { opacity: 0.52; }
                50% { opacity: 1.0; }
                100% { opacity: 0.52; }
            }

            @media (max-width: 1100px) {
                .kpi-stack { width: 24%; min-width: 180px; }
                .scene-title { font-size: 1.2rem; }
                .hud-card { font-size: 1.1rem; }
            }

            @media (max-width: 860px) {
                .scene-wrap { height: 70vh; min-height: 560px; }
                .kpi-stack {
                    position: absolute;
                    width: 45%;
                    right: 1.5%;
                    top: 11%;
                }
                .kpi-title { font-size: 1rem; }
                .kpi-value { font-size: 1.2rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def to_data_uri(image_path: Path) -> str:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def load_scene_images(base_dir: Path) -> dict[str, Path]:
    img_dir = base_dir / "img_dtc"
    files = sorted(img_dir.glob("*.png"))
    if len(files) < 4:
        raise FileNotFoundError("At least 4 PNG files are required in img_dtc")

    # Mapped to likely scene order from provided visual set.
    return {
        "Unified Command": files[3],
        "Grid Balancing": files[5],
        "Unlinked Relay": files[0],
        "V2I Greenwave": files[2],
    }


def render_scene_html(title: str, background_uri: str, overlays: str, show_kpi: bool = True) -> str:
    kpi_html = ""
    if show_kpi:
        kpi_html = """
        <div class='kpi-stack'>
            <div class='kpi'><p class='kpi-title'>Fleet Optimization</p><p class='kpi-value'>94%</p></div>
            <div class='kpi'><p class='kpi-title'>Energy Grid Load</p><p class='kpi-value'>Stable</p></div>
            <div class='kpi'><p class='kpi-title'>Active Alerts</p><p class='kpi-value warn'>2 (Minor)</p></div>
        </div>
        """

    return f"""
    <div class='scene-wrap'>
        <div class='scene-bg' style='background-image:url("{background_uri}")'></div>
        <div class='scene-overlay'></div>
        <div class='scene-title'>{title}</div>
        {kpi_html}
        {overlays}
    </div>
    """


def unified_overlays() -> str:
    return """
    <div class='bus-glow bus-blue' style='left: 14%; top: 31%; transform: rotate(-12deg);'></div>
    <div class='bus-glow bus-blue' style='left: 27%; top: 64%; transform: rotate(-23deg);'></div>
    <div class='bus-glow bus-green' style='left: 56%; top: 39%; transform: rotate(16deg);'></div>
    <div class='bus-glow bus-green' style='left: 68%; top: 43%; transform: rotate(12deg);'></div>

    <div class='beam' style='left: 58%; top: 45%; width: 15.5%; transform: rotate(15deg);'></div>

    <div class='hud-card' style='left: 18.5%; top: 35%;'>Bus ID: DTC-402EV\nBattery: 82%\nNext Relay: 7 mins</div>
    <div class='hud-card' style='left: 61.5%; top: 50.5%;'>Automated Unlinked Relay\nHandover in Progress</div>
    """


def grid_overlays() -> str:
    return """
    <div class='bus-glow bus-red' style='left: 21%; top: 57%; transform: rotate(14deg);'></div>
    <div class='bus-glow bus-red' style='left: 34%; top: 52%; transform: rotate(9deg);'></div>
    <div class='bus-glow bus-red' style='left: 50%; top: 63%; transform: rotate(-7deg);'></div>
    <div class='bus-glow bus-red' style='left: 60%; top: 69%; transform: rotate(6deg);'></div>

    <div class='beam red' style='left: 24%; top: 58%; width: 26%; transform: rotate(-8deg);'></div>
    <div class='beam red' style='left: 36%; top: 54%; width: 28%; transform: rotate(13deg);'></div>
    <div class='beam red' style='left: 52%; top: 64%; width: 19%; transform: rotate(-26deg);'></div>

    <div class='hud-card' style='left: 50%; top: 18%; border-color: rgba(255,95,118,0.55); background: rgba(58,9,17,0.62); color: #ffd6dd;'>Local Grid Demand: Critical (120% capacity)</div>
    <div class='hud-card' style='left: 63%; top: 39%; border-color: rgba(255,95,118,0.55); background: rgba(58,9,17,0.62); color: #ffd6dd;'>Grid Stabilizing\nV2G Activated</div>
    <div class='hud-card' style='left: 64%; top: 56%; border-color: rgba(255,95,118,0.55); background: rgba(58,9,17,0.62); color: #ffd6dd;'>Bus 19-EV\nHigh Thermal Risk</div>
    """


def relay_overlays() -> str:
    return """
    <div class='bus-glow bus-red' style='left: 31%; top: 50%; transform: rotate(18deg);'></div>
    <div class='bus-glow bus-blue' style='left: 57%; top: 45%; transform: rotate(22deg);'></div>

    <div class='beam' style='left: 37%; top: 52%; width: 20%; transform: rotate(-8deg);'></div>

    <div class='hud-card' style='left: 29%; top: 31%;'>Arriving Bus (DTC-101E)\nAgent ID: DTC-101E\nThermal Health: COOL\nArrival ETA: On Time</div>
    <div class='hud-card' style='left: 58%; top: 37%;'>Relay Crew (ID: B32)\nRest Verified\nDuty Start: 0 mins</div>
    """


def v2i_overlays() -> str:
    return """
    <div class='bus-glow bus-red' style='left: 30%; top: 58%; width: 90px; height: 32px; transform: rotate(-12deg);'></div>
    <div class='beam' style='left: 39%; top: 61%; width: 24%; transform: rotate(-20deg);'></div>

    <div class='hud-card' style='left: 30%; top: 40%; border-color: rgba(255,95,118,0.55); background: rgba(58,9,17,0.62); color: #ffd6dd;'>Late: 4.5 mins\nV2I Handshake Request Active</div>
    <div class='hud-card' style='left: 56%; top: 26%;'>Green Light Priority Granted\n(15s Extension)</div>
    """


def render_scene(page: str, scene_images: dict[str, Path]) -> None:
    bg_uri = to_data_uri(scene_images[page])
    if page == "Unified Command":
        html = render_scene_html("Kashmere Gate ISBT", bg_uri, unified_overlays(), show_kpi=True)
    elif page == "Grid Balancing":
        html = render_scene_html("Okhla Depot, ISBT", bg_uri, grid_overlays(), show_kpi=True)
    elif page == "Unlinked Relay":
        html = render_scene_html("Sarai Kale Khan ISBT", bg_uri, relay_overlays(), show_kpi=True)
    else:
        html = render_scene_html("Tilak Marg, Delhi", bg_uri, v2i_overlays(), show_kpi=True)

    st.markdown(html, unsafe_allow_html=True)


def main() -> None:
    inject_theme()

    st.sidebar.title("Unified DTC Nav-Sync AI")
    st.sidebar.caption("War Room | Cyber-Physical Digital Twin")
    page = st.sidebar.radio(
        "Dashboard View",
        ["Unified Command", "Grid Balancing", "Unlinked Relay", "V2I Greenwave"],
        index=0,
    )

    scene_images = load_scene_images(Path(__file__).resolve().parent)
    render_scene(page, scene_images)


if __name__ == "__main__":
    main()
