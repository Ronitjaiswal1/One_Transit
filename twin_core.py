from __future__ import annotations

from pathlib import Path

import pandas as pd


DEFAULT_BUS_COLOR = [0, 179, 255, 220]


def _as_text_series(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("")


def parse_gtfs_time_to_seconds(value: object) -> int:
    """Parse GTFS HH:MM:SS into seconds (supports hour values >= 24)."""
    if pd.isna(value):
        return 0

    raw = str(value).strip()
    parts = raw.split(":")
    if len(parts) != 3:
        return 0

    try:
        hour, minute, second = (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return 0

    return (hour * 3600) + (minute * 60) + second


def format_seconds_to_hhmmss(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))
    hour = (total_seconds // 3600) % 24
    minute = (total_seconds % 3600) // 60
    second = total_seconds % 60
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def load_gtfs_data(data_dir: str = ".") -> dict[str, pd.DataFrame]:
    base = Path(data_dir)

    stops = pd.read_csv(base / "stops.txt", dtype={"stop_id": "string"})
    stop_times = pd.read_csv(
        base / "stop_times.txt",
        dtype={"trip_id": "string", "stop_id": "string"},
    )
    trips = pd.read_csv(
        base / "trips.txt",
        dtype={"trip_id": "string", "route_id": "string", "shape_id": "string", "service_id": "string"},
    )
    routes = pd.read_csv(base / "routes.txt", dtype={"route_id": "string"})
    shapes = pd.read_csv(base / "shapes.txt", dtype={"shape_id": "string"})

    stop_times["stop_sequence"] = pd.to_numeric(stop_times["stop_sequence"], errors="coerce").fillna(0)
    stop_times["arrival_secs"] = stop_times["arrival_time"].map(parse_gtfs_time_to_seconds)
    stop_times["departure_secs"] = stop_times["departure_time"].map(parse_gtfs_time_to_seconds)
    stop_times = stop_times.sort_values(["trip_id", "stop_sequence"]).reset_index(drop=True)

    stops["stop_lat"] = pd.to_numeric(stops["stop_lat"], errors="coerce")
    stops["stop_lon"] = pd.to_numeric(stops["stop_lon"], errors="coerce")
    stops = stops.dropna(subset=["stop_lat", "stop_lon"]).reset_index(drop=True)

    shapes["shape_pt_sequence"] = pd.to_numeric(shapes["shape_pt_sequence"], errors="coerce").fillna(0)
    shapes["shape_pt_lat"] = pd.to_numeric(shapes["shape_pt_lat"], errors="coerce")
    shapes["shape_pt_lon"] = pd.to_numeric(shapes["shape_pt_lon"], errors="coerce")
    shapes = shapes.dropna(subset=["shape_pt_lat", "shape_pt_lon"]).reset_index(drop=True)

    return {
        "stops": stops,
        "stop_times": stop_times,
        "trips": trips,
        "routes": routes,
        "shapes": shapes,
    }


def get_available_services(gtfs_data: dict[str, pd.DataFrame]) -> list[str]:
    services = _as_text_series(gtfs_data["trips"]["service_id"])
    return sorted({service for service in services.tolist() if service})


def filter_trips(
    gtfs_data: dict[str, pd.DataFrame],
    route_ids: list[str] | None = None,
    service_ids: list[str] | None = None,
    limit: int = 100,
) -> pd.DataFrame:
    trips = gtfs_data["trips"].copy()

    if route_ids:
        route_ids_set = {str(route_id) for route_id in route_ids}
        trips = trips[trips["route_id"].astype("string").isin(route_ids_set)]

    if service_ids:
        service_ids_set = {str(service_id) for service_id in service_ids}
        trips = trips[trips["service_id"].astype("string").isin(service_ids_set)]

    trip_stop_counts = gtfs_data["stop_times"].groupby("trip_id", dropna=False).size()
    valid_trip_ids = set(trip_stop_counts[trip_stop_counts >= 2].index.astype("string").tolist())
    trips = trips[trips["trip_id"].astype("string").isin(valid_trip_ids)]

    return trips.head(max(1, int(limit))).reset_index(drop=True)


def _route_color_to_rgba(route_color: object) -> list[int]:
    if not isinstance(route_color, str) or len(route_color.strip()) != 6:
        return [80, 120, 255, 140]

    color = route_color.strip()
    try:
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
    except ValueError:
        return [80, 120, 255, 140]

    return [red, green, blue, 150]


def build_route_paths(gtfs_data: dict[str, pd.DataFrame], trip_ids: list[str]) -> pd.DataFrame:
    if not trip_ids:
        return pd.DataFrame(columns=["shape_id", "route_id", "path", "color"])

    trips = gtfs_data["trips"]
    routes = gtfs_data["routes"]
    shapes = gtfs_data["shapes"]

    selected = trips[trips["trip_id"].astype("string").isin({str(trip_id) for trip_id in trip_ids})]
    selected = selected.dropna(subset=["shape_id"]).drop_duplicates(subset=["shape_id"]) 

    if selected.empty:
        return pd.DataFrame(columns=["shape_id", "route_id", "path", "color"])

    selected = selected.merge(routes[["route_id", "route_color"]], on="route_id", how="left")

    rows: list[dict[str, object]] = []
    for _, row in selected.iterrows():
        shape_id = str(row["shape_id"])
        shape_points = shapes[shapes["shape_id"].astype("string") == shape_id].sort_values("shape_pt_sequence")
        if len(shape_points) < 2:
            continue

        path = shape_points[["shape_pt_lon", "shape_pt_lat"]].values.tolist()
        rows.append(
            {
                "shape_id": shape_id,
                "route_id": str(row["route_id"]),
                "path": path,
                "color": _route_color_to_rgba(row.get("route_color")),
            }
        )

    return pd.DataFrame(rows)


def _visits_to_color(visits: int, max_visits: int) -> list[int]:
    if max_visits <= 0:
        return [59, 130, 246, 180]

    intensity = min(1.0, float(visits) / float(max_visits))
    red = int(40 + (210 * intensity))
    green = int(150 - (90 * intensity))
    blue = int(240 - (140 * intensity))
    return [red, green, blue, 190]


def build_stop_columns(
    gtfs_data: dict[str, pd.DataFrame],
    route_ids: list[str] | None = None,
    max_stops: int = 900,
) -> pd.DataFrame:
    stops = gtfs_data["stops"][["stop_id", "stop_name", "stop_lat", "stop_lon"]].copy()
    stop_times = gtfs_data["stop_times"][["trip_id", "stop_id"]].copy()
    trips = gtfs_data["trips"][["trip_id", "route_id"]].copy()

    if route_ids:
        route_ids_set = {str(route_id) for route_id in route_ids}
        trips = trips[trips["route_id"].astype("string").isin(route_ids_set)]

    stop_visits = stop_times.merge(trips, on="trip_id", how="inner").groupby("stop_id", dropna=False).size()
    if stop_visits.empty:
        return pd.DataFrame(columns=["stop_name", "lat", "lon", "visits", "elevation", "color"])

    stop_summary = stops.merge(
        stop_visits.rename("visits").reset_index(),
        on="stop_id",
        how="inner",
    )
    stop_summary = stop_summary.sort_values("visits", ascending=False).head(max(1, int(max_stops)))

    max_visits = int(stop_summary["visits"].max()) if not stop_summary.empty else 1
    stop_summary["elevation"] = stop_summary["visits"].map(lambda value: max(60, min(int(value) * 10, 720)))
    stop_summary["color"] = stop_summary["visits"].map(lambda value: _visits_to_color(int(value), max_visits))
    stop_summary = stop_summary.rename(columns={"stop_lat": "lat", "stop_lon": "lon"})

    return stop_summary[["stop_name", "lat", "lon", "visits", "elevation", "color"]]


def _interpolate_trip_position(trip_df: pd.DataFrame, target_seconds: int) -> tuple[float, float, float] | None:
    if trip_df.empty:
        return None

    if len(trip_df) == 1:
        row = trip_df.iloc[0]
        return float(row["stop_lat"]), float(row["stop_lon"]), 0.0

    first = trip_df.iloc[0]
    last = trip_df.iloc[-1]
    if target_seconds <= int(first["departure_secs"]):
        return float(first["stop_lat"]), float(first["stop_lon"]), 0.0
    if target_seconds >= int(last["arrival_secs"]):
        return float(last["stop_lat"]), float(last["stop_lon"]), 1.0

    segment_count = max(1, len(trip_df) - 1)
    for idx in range(segment_count):
        current_row = trip_df.iloc[idx]
        next_row = trip_df.iloc[idx + 1]

        start_secs = int(current_row["departure_secs"])
        end_secs = int(next_row["arrival_secs"])
        if end_secs <= start_secs:
            end_secs = start_secs + 1

        if start_secs <= target_seconds <= end_secs:
            ratio = float(target_seconds - start_secs) / float(end_secs - start_secs)
            lat = float(current_row["stop_lat"]) + ratio * (float(next_row["stop_lat"]) - float(current_row["stop_lat"]))
            lon = float(current_row["stop_lon"]) + ratio * (float(next_row["stop_lon"]) - float(current_row["stop_lon"]))
            progress = (idx + ratio) / float(segment_count)
            return lat, lon, progress

    return None


def _status_from_battery(battery_percent: float) -> str:
    if battery_percent < 25:
        return "Low Battery"
    if battery_percent < 45:
        return "Charging Soon"
    return "Operational"


def _status_to_color(status: str) -> list[int]:
    if status == "Low Battery":
        return [255, 87, 34, 220]
    if status == "Charging Soon":
        return [255, 193, 7, 220]
    return DEFAULT_BUS_COLOR


def simulate_bus_positions(
    gtfs_data: dict[str, pd.DataFrame],
    trip_ids: list[str],
    target_seconds: int,
) -> pd.DataFrame:
    if not trip_ids:
        return pd.DataFrame(columns=["trip_id", "route_id", "route_short_name", "lat", "lon", "status", "battery", "color"])

    selected_trip_ids = {str(trip_id) for trip_id in trip_ids}
    stop_times = gtfs_data["stop_times"]
    stops = gtfs_data["stops"][["stop_id", "stop_name", "stop_lat", "stop_lon"]]
    trips = gtfs_data["trips"][["trip_id", "route_id"]]
    routes = gtfs_data["routes"][["route_id", "route_short_name"]]

    merged = stop_times[stop_times["trip_id"].astype("string").isin(selected_trip_ids)].merge(
        stops,
        on="stop_id",
        how="inner",
    )

    if merged.empty:
        return pd.DataFrame(columns=["trip_id", "route_id", "route_short_name", "lat", "lon", "status", "battery", "color"])

    merged = merged.sort_values(["trip_id", "stop_sequence"]).reset_index(drop=True)
    trip_route = trips.merge(routes, on="route_id", how="left")

    rows: list[dict[str, object]] = []
    for trip_id, trip_df in merged.groupby("trip_id"):
        position = _interpolate_trip_position(trip_df, int(target_seconds))
        if position is None:
            continue

        lat, lon, progress = position
        battery = max(15.0, 100.0 - (progress * 78.0))
        status = _status_from_battery(battery)

        info = trip_route[trip_route["trip_id"].astype("string") == str(trip_id)]
        if info.empty:
            route_id = ""
            route_short_name = ""
        else:
            route_id = str(info.iloc[0]["route_id"])
            route_short_name = str(info.iloc[0].get("route_short_name", ""))

        rows.append(
            {
                "trip_id": str(trip_id),
                "route_id": route_id,
                "route_short_name": route_short_name,
                "lat": lat,
                "lon": lon,
                "status": status,
                "battery": round(float(battery), 1),
                "color": _status_to_color(status),
            }
        )

    return pd.DataFrame(rows)