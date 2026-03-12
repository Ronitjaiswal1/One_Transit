from __future__ import annotations

from datetime import datetime
from pathlib import Path
import time

import pydeck as pdk
import streamlit as st

from twin_core import (
    build_route_paths,
    build_stop_columns,
    filter_trips,
    format_seconds_to_hhmmss,
    get_available_services,
    load_gtfs_data,
    parse_gtfs_time_to_seconds,
    simulate_bus_positions,
)


st.set_page_config(page_title="DTC Delhi 3D Digital Twin", layout="wide")
st.title("DTC Delhi Open Transit Data: 3D Digital Twin")
st.caption("Live simulation generated from GTFS files in this workspace")


@st.cache_data(show_spinner=False)
def cached_gtfs(data_dir: str) -> dict:
    return load_gtfs_data(data_dir)


def _records(df):
    # pydeck in this environment serializes plain dict records more reliably than DataFrames.
    return df.where(df.notna(), None).to_dict(orient="records")


data_path = Path(__file__).resolve().parent
gtfs = cached_gtfs(str(data_path))

routes_df = gtfs["routes"].copy()
routes_df["label"] = routes_df["route_short_name"].fillna(routes_df["route_id"]).astype(str)
route_options = routes_df[["route_id", "label"]].drop_duplicates().sort_values("label")
route_label_map = {
    str(route_id): str(label)
    for route_id, label in route_options[["route_id", "label"]].itertuples(index=False, name=None)
}

default_routes = route_options["route_id"].astype(str).head(8).tolist()

st.sidebar.header("Twin Controls")
selected_routes = st.sidebar.multiselect(
    "Routes",
    options=route_options["route_id"].astype(str).tolist(),
    default=default_routes,
    format_func=lambda rid: route_label_map.get(str(rid), str(rid)),
)

all_services = get_available_services(gtfs)
selected_services = st.sidebar.multiselect(
    "Service IDs",
    options=all_services,
    default=all_services,
)

max_trips = st.sidebar.slider("Max Active Trips", min_value=20, max_value=400, value=140, step=20)
vehicle_mode = st.sidebar.selectbox(
    "Vehicle Render Mode",
    options=["Points", "Bus Icons", "3D Vehicle Icons"],
    index=2,
)

if "sim_seconds" not in st.session_state:
    now_hms = datetime.now().strftime("%H:%M:%S")
    st.session_state.sim_seconds = parse_gtfs_time_to_seconds(now_hms)
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False

clock_col_1, clock_col_2, clock_col_3 = st.sidebar.columns(3)
if clock_col_1.button("Play", use_container_width=True):
    st.session_state.is_playing = True
if clock_col_2.button("Pause", use_container_width=True):
    st.session_state.is_playing = False
if clock_col_3.button("Reset", use_container_width=True):
    st.session_state.sim_seconds = parse_gtfs_time_to_seconds(datetime.now().strftime("%H:%M:%S"))

target_seconds = st.sidebar.slider(
    "Simulation Timeline (seconds of day)",
    min_value=0,
    max_value=86399,
    value=int(st.session_state.sim_seconds),
    step=1,
)

if target_seconds != int(st.session_state.sim_seconds):
    st.session_state.sim_seconds = int(target_seconds)

manual_time_text = st.sidebar.text_input(
    "Jump to Time (HH:MM:SS)",
    value=format_seconds_to_hhmmss(int(st.session_state.sim_seconds)),
)
if st.sidebar.button("Apply Time", use_container_width=True):
    jump_seconds = parse_gtfs_time_to_seconds(manual_time_text)
    if jump_seconds == 0 and manual_time_text != "00:00:00":
        st.sidebar.warning("Invalid HH:MM:SS format")
    else:
        st.session_state.sim_seconds = int(jump_seconds)

st.sidebar.caption(
    f"Clock: {format_seconds_to_hhmmss(int(st.session_state.sim_seconds))} | "
    f"{'Playing' if st.session_state.is_playing else 'Paused'}"
)

target_seconds = int(st.session_state.sim_seconds)

filtered_trips = filter_trips(
    gtfs_data=gtfs,
    route_ids=selected_routes,
    service_ids=selected_services,
    limit=max_trips,
)
trip_ids = filtered_trips["trip_id"].astype(str).tolist()

route_paths = build_route_paths(gtfs, trip_ids)
stop_columns = build_stop_columns(gtfs, route_ids=selected_routes, max_stops=700)
bus_positions = simulate_bus_positions(gtfs, trip_ids, target_seconds)

left, middle, right = st.columns(3)
left.metric("Routes Selected", f"{len(selected_routes)}")
middle.metric("Trips Simulated", f"{len(trip_ids)}")
right.metric("Buses Visible", f"{len(bus_positions)}", format_seconds_to_hhmmss(target_seconds))

if stop_columns.empty:
    st.error("No valid stop data available. Check GTFS files.")
    st.stop()

center_lat = float(stop_columns["lat"].mean())
center_lon = float(stop_columns["lon"].mean())
view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=10.8,
    pitch=52,
    bearing=8,
)

layers: list[pdk.Layer] = []

if not route_paths.empty:
    route_records = _records(route_paths)
    layers.append(
        pdk.Layer(
            "PathLayer",
            route_records,
            get_path="path",
            get_color="color",
            width_scale=4,
            width_min_pixels=2,
            pickable=True,
            auto_highlight=True,
        )
    )

stop_records = _records(stop_columns)
layers.append(
    pdk.Layer(
        "ColumnLayer",
        stop_records,
        get_position="[lon, lat]",
        get_elevation="elevation",
        elevation_scale=1,
        radius=55,
        get_fill_color="color",
        pickable=True,
        extruded=True,
        auto_highlight=True,
    )
)

if not bus_positions.empty:
    if vehicle_mode == "Points":
        bus_records = _records(bus_positions)
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                bus_records,
                get_position="[lon, lat]",
                get_color="color",
                get_radius=110,
                pickable=True,
            )
        )
    elif vehicle_mode == "Bus Icons":
        icon_data = bus_positions.copy()
        icon_data["icon"] = icon_data.apply(
            lambda _: {
                "url": "https://cdn-icons-png.flaticon.com/512/61/61231.png",
                "width": 512,
                "height": 512,
                "anchorY": 512,
            },
            axis=1,
        )
        icon_records = _records(icon_data)
        layers.append(
            pdk.Layer(
                "IconLayer",
                icon_records,
                get_icon="icon",
                get_position="[lon, lat]",
                get_size=4,
                size_scale=7,
                pickable=True,
            )
        )
    else:
        icon_3d = bus_positions.copy()
        icon_3d["vehicle_height"] = 150
        icon_3d_records = _records(icon_3d)
        layers.append(
            pdk.Layer(
                "ColumnLayer",
                icon_3d_records,
                get_position="[lon, lat]",
                get_elevation="vehicle_height",
                elevation_scale=1,
                radius=32,
                get_fill_color="color",
                pickable=True,
                extruded=True,
                auto_highlight=True,
            )
        )

tooltip = {
    "html": (
        "<b>Route:</b> {route_short_name}<br/>"
        "<b>Trip:</b> {trip_id}<br/>"
        "<b>Status:</b> {status}<br/>"
        "<b>Battery:</b> {battery}%<br/>"
        "<b>Stop:</b> {stop_name}<br/>"
        "<b>Visits:</b> {visits}"
    ),
    "style": {"backgroundColor": "#101820", "color": "#ffffff"},
}

deck = pdk.Deck(
    map_style="light",
    initial_view_state=view_state,
    layers=layers,
    tooltip=tooltip,
)

st.pydeck_chart(deck, use_container_width=True)

if st.session_state.is_playing:
    time.sleep(1)
    st.session_state.sim_seconds = (int(st.session_state.sim_seconds) + 1) % 86400
    st.rerun()

with st.expander("Data Summary"):
    st.write("Routes in feed:", int(gtfs["routes"].shape[0]))
    st.write("Trips in feed:", int(gtfs["trips"].shape[0]))
    st.write("Stops in feed:", int(gtfs["stops"].shape[0]))
    st.write("Shape points:", int(gtfs["shapes"].shape[0]))