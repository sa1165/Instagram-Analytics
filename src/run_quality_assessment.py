"""Run data quality assessment and save report.

This script is intended to be executed as part of the ETL pipeline.
"""

import pandas as pd
from pathlib import Path
import json

# Import the ingestion and data_quality modules using relative imports
import sys
sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from ingestion import load_raw_data
from data_quality import assess_quality, save_report

def main():
    df = load_raw_data()
    report = assess_quality(df)
    # Save report (function already writes to file)
    save_report(report)
    # Also print summary to console for quick view
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()

