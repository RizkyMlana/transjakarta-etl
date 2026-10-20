import pandas as pd
from extract import extract_all

def profile_data(df: pd.DataFrame) -> pd.DataFrame:
    total_rows = len(df)

    profile = pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.astype(str).values,
        "total_rows": total_rows,
        "missing_count": df.isna().sum().values,
        "unique_count": df.nunique(dropna=True).values,
    })

    profile["missing_pct"] = (
        profile["missing_count"] / total_rows * 100
        if total_rows > 0 else 0.0
    )
    return profile


def profile_all(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    results = {}

    for name, df in datasets.items():
        print(f"\n{'=' * 50}")
        print(f"Dataset: {name}")
        print(f"Shape: {df.shape}")
        print(f"Duplicate rows: {df.duplicated().sum()}")
        print(f"{'=' * 50}")

        summary = profile_data(df)
        print(summary.to_string(index=False))

        results[name] = summary
    return results
def profile_relationship(datasets: dict[str,pd.DataFrame]):
    stops = datasets["stops"]
    routes = datasets["routes"]
    trips = datasets["trips"]
    stop_times = datasets["stop_times"]

    dupl_sequences = stop_times.duplicated(
        subset=["trip_id", "stop_sequence"]
    ).sum()

    invalid_route_ids = (
        ~trips["route_id"].isin(routes["route_id"])
    ).sum()
    invalid_trip_ids = (
        ~stop_times["trip_id"].isin(trips["trip_id"])
    ).sum()

    invalid_stop_ids = (
        ~stop_times["stop_id"].isin(stops["stop_id"])
    ).sum()
    unused_stops = (
        ~stops["stop_id"].isin(stop_times["stop_id"])
    ).sum()

    print("Duplicate trip + stop_sequence:", dupl_sequences)
    print("Invalid route references:", invalid_route_ids)
    print("Invalid trip references:", invalid_trip_ids)
    print("Invalid stop references:", invalid_stop_ids)
    print("Stops not referenced by stop_times:", unused_stops)

def profile_unused_stops(datasets:dict[str, pd.DataFrame]) -> pd.DataFrame:
    stops = datasets["stops"]
    stop_times = datasets["stop_times"]

    unused_stops = stops[
        ~stops["stop_id"].isin(stop_times["stop_id"])
    ].copy()

    print(f"Unused stops: {len(unused_stops)}")
    print("\nLocation type distribution:")
    print(
        unused_stops["location_type"]
        .value_counts(dropna=False)
    )

    print("\nSample unused stops:")
    print(
        unused_stops[
            ["stop_id", "stop_name", "location_type", "parent_station"]
        ].head(20)
    )

    return unused_stops


def profile_station_hierarchy(
        datasets: dict[str, pd.DataFrame]
) -> None:
    stops = datasets["stops"]
    stations = stops[stops["location_type"] == "1"]
    child_stops = stops[stops["parent_station"].notna()]

    invalid_parents = child_stops[
        ~child_stops["parent_station"].isin(stations["stop_id"])
    ]

    children_per_station = (
        child_stops.groupby("parent_station").size().sort_values(ascending=False)
    )
    stations_without_children = stations[
        ~stations["stop_id"].isin(child_stops["parent_station"])
    ]
    print("Total stations:", len(stations))
    print("Total child stops:", len(child_stops))
    print("Invalid parent references:", len(invalid_parents))
    print("Stations without children:", len(stations_without_children))

    print("\nTop 10 stations by child stops:")
    print(children_per_station.head(10))
    print(children_per_station.describe())

if __name__ == "__main__":
    datasets = extract_all()
    profiles = profile_all(datasets)
    profile_relationship(datasets)
    unused_stops = profile_unused_stops(datasets)
    profile_station_hierarchy(datasets)
        