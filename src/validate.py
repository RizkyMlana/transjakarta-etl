import pandas as pd

def validate_stops(df: pd.DataFrame) -> None:
    assert df["stop_id"].notna().all(), "Null stop_id"
    assert df["stop_id"].is_unique, "Duplicate stop_id"
    assert df["stop_lat"].between(-90, 90).all(), \
        "Invalid latitude"
    assert df["stop_lon"].between(-180, 180).all(), \
        "Invalid longitude"

def validate_routes(df: pd.DataFrame) -> None:
    assert df["route_id"].notna().all(), "Null route_id"
    assert df["route_id"].is_unique, "Duplicate route_id"

def validate_route_stop_mapping(
        df: pd.DataFrame,
        stops: pd.DataFrame,
        routes: pd.DataFrame
) -> None:
    assert not df[["route_id", "stop_id"]].isna().any().any(), \
        "Null mapping key"
    assert not df.duplicated(["route_id", "stop_id"]).any(), \
        "Duplicate route-stop pair"
    assert df["stop_id"].isin(stops["stop_id"]).all(), \
        "Invalid stop reference"
    assert df["route_id"].isin(routes["route_id"]).all(), \
        "Invalid route reference"


def validate_station_features(
        df: pd.DataFrame,
        stops: pd.DataFrame,
) -> None:
    assert df["station_id"].notna().all(), "Null station_id"
    assert df["station_id"].is_unique, "Duplicate station_id"
    assert df["station_id"].isin(stops["stop_id"]).all(), \
        "Invalid station reference"
    assert df["n_child_stops"].ge(1).all(), \
        "Station without child stops"
    assert df[["n_routes", "n_trips"]].ge(0).all().all(), \
        "Negative route or trip counts"

