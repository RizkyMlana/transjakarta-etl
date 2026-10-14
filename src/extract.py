from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"

def extract_data(filename: str) -> pd.DataFrame:
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"file not found: {file_path}")
    return pd.read_csv(file_path, dtype=str)



df = extract_data("routes.txt")
print(df.head())