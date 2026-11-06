import pandas as pd, json, sys
path = r"C:\Users\Sanjeev\Documents\Projects\Instagram analytics\Instagram_Analytics.csv"
try:
    df = pd.read_csv(path)
except Exception as e:
    print('Error loading CSV:', e)
    sys.exit(1)
# Basic info
info = {
    "rows": df.shape[0],
    "columns": df.shape[1],
    "column_names": list(df.columns),
    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    "missing_counts": df.isna().sum().to_dict(),
    "head": df.head().to_dict(orient='records')
}
print(json.dumps(info, indent=2))

