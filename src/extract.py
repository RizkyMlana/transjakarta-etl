from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"

files = {
    "stops.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt"
}

def extract_data(filename: str) -> pd.DataFrame:
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"file not found: {file_path}")
    return pd.read_csv(file_path, dtype=str)

def extract_all() -> dict[str, pd.DataFrame]:
    datasets = {}

    for filename in files:
        name = Path(filename).stem
        datasets[name] = extract_data(filename)

    return datasets


if __name__ == "__main__":
    datasets = extract_all()

    for name, df in datasets.items():
        print(f"{name}: {df.shape}")
        assert not df.empty, f"{name} is empty"

        