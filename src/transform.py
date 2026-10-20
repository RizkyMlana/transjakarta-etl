import pandas as pd
from extract import extract_all
from validate import (
    validate_stops,
    validate_routes,
    validate_route_stop_mapping,
    validate_station_features
)

def transform_stops(stops: pd.DataFrame) -> pd.DataFrame:
    df = stops[
        ["stop_id",
        "stop_name",
        "stop_lat",
        "stop_lon",
        "location_type",
        "parent_station",]
    ].copy()

    df["stop_lat"] = pd.to_numeric(
        df["stop_lat"], errors="coerce"
    )
    df["stop_lon"] = pd.to_numeric(
        df["stop_lon"], errors="coerce"
    )

    df["location_type"] = df["location_type"].fillna("0")

    for col in ["stop_id", "stop_name", "parent_station"]:
        df[col] = df[col].str.strip()

    return df

def transform_routes(routes: pd.DataFrame) -> pd.DataFrame:
    df= routes[
        [
            "route_id",
            "route_short_name",
            "route_long_name",
            "route_type",
        ]
    ].copy()

    for col in ["route_id", "route_short_name", "route_long_name"]:
        df[col] = df[col].str.strip()

    return df


def transform_route_stop_mapping(
    stop_times: pd.DataFrame,
    trips: pd.DataFrame,
    dim_routes: pd.DataFrame,
    dim_stops: pd.DataFrame,
) -> pd.DataFrame:

    stop_times_df = stop_times[["trip_id", "stop_id"]].copy()
    trips_df = trips[["trip_id", "route_id"]].copy()

    
    mapping = stop_times_df.merge(
        trips_df,
        on="trip_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    if (mapping["_merge"] != "both").any():
        raise ValueError("Ada trip_id yang tidak ditemukan di trips")

    mapping = mapping.drop(columns="_merge")

    if not mapping["route_id"].isin(dim_routes["route_id"]).all():
        raise ValueError("Ada route_id yang tidak valid")

    if not mapping["stop_id"].isin(dim_stops["stop_id"]).all():
        raise ValueError("Ada stop_id yang tidak valid")

    mapping = (
        mapping[["route_id", "stop_id"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return mapping


def transform_station_features(
    dim_stops: pd.DataFrame,
    route_stop_mapping: pd.DataFrame,
    stop_times: pd.DataFrame,
) -> pd.DataFrame:

    stations = dim_stops[
        dim_stops["location_type"] == "1"
    ][["stop_id", "stop_name", "stop_lat", "stop_lon"]].copy()

    stations = stations.rename(columns={
        "stop_id": "station_id",
        "stop_name": "station_name",
        "stop_lat": "latitude",
        "stop_lon": "longitude",
    })

    children = dim_stops[
        dim_stops["parent_station"].notna()
    ][["stop_id", "parent_station"]].copy()

    children = children.rename(columns={
        "parent_station": "station_id"
    })

    child_counts = (
        children.groupby("station_id")["stop_id"]
        .nunique()
        .rename("n_child_stops")
    )

    route_counts = (
        children.merge(
            route_stop_mapping,
            on="stop_id",
            how="left",
            validate="one_to_many",
        )
        .groupby("station_id")["route_id"]
        .nunique()
        .rename("n_routes")
    )
    trip_counts = (
        children.merge(
            stop_times[["stop_id", "trip_id"]],
            on="stop_id",
            how="left",
            validate="one_to_many",
        )
        .groupby("station_id")["trip_id"]
        .nunique()
        .rename("n_trips")
    )
    features = (
        stations
        .merge(child_counts, on="station_id", how="left")
        .merge(route_counts, on="station_id", how="left")
        .merge(trip_counts, on="station_id", how="left")
    )

    count_columns = ["n_child_stops", "n_routes", "n_trips"]

    features[count_columns] = (
        features[count_columns].fillna(0).astype(int)
    )

    return features

if __name__ == "__main__":
    datasets = extract_all()
    dim_stops = transform_stops(datasets["stops"])
    dim_routes = transform_routes(datasets["routes"])
    route_stop_mapping = transform_route_stop_mapping(
        datasets["stop_times"],
        datasets["trips"],
        dim_routes,
        dim_stops,
    )
    station_features = transform_station_features(
        dim_stops,
        route_stop_mapping,
        datasets["stop_times"]
    )

    validate_stops(dim_stops)
    validate_routes(dim_routes)
    validate_route_stop_mapping(
        route_stop_mapping,
        dim_stops,
        dim_routes,
    )
    validate_station_features(
        station_features,
        dim_stops
    )
    print("All data validations passed!")