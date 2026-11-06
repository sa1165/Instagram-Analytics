"""Data Ingestion Module.
Responsible for reading the raw Instagram dataset without modifying it,
validating initial schema, and extracting basic statistical descriptions.
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd


def load_raw_dataset(filepath: str | Path = "data/raw/Instagram_Analytics.csv") -> pd.DataFrame:
    """Load the raw Instagram Analytics CSV file.
    Preserves raw data integrity without in-place modification.
    """
    path = Path(filepath)
    if not path.exists():
        # Fallback to current directory if not found in data/raw
        alt_path = Path("Instagram_Analytics.csv")
        if alt_path.exists():
            path = alt_path
        else:
            raise FileNotFoundError(f"Raw dataset could not be located at {filepath} or {alt_path}")

    # Read original CSV without mutation
    df = pd.read_csv(path)
    return df


def get_dataset_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate and return dataset structural metrics, schema, and sample stats."""
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

    overview = {
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "columns": list(df.columns),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "unique_counts": {col: int(df[col].nunique()) for col in df.columns},
        "categorical_unique_counts": {col: int(df[col].nunique()) for col in categorical_cols},
        "descriptive_stats": df.describe().to_dict(),
        "memory_usage_mb": float(df.memory_usage(deep=True).sum() / (1024 * 1024)),
    }
    return overview


if __name__ == "__main__":
    df_raw = load_raw_dataset()
    overview = get_dataset_overview(df_raw)
    print(f"Loaded raw dataset with {overview['total_rows']} rows and {overview['total_columns']} columns.")
    print(f"Categorical unique counts: {overview['categorical_unique_counts']}")
