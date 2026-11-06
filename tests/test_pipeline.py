"""Unit and Integration Tests for the Instagram Analytics Pipeline.
Validates ingestion, data quality rules, cleaning logic, feature engineering, and database roundtrips.
"""

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

from src.ingestion import load_raw_dataset, get_dataset_overview
from src.data_quality import assess_data_quality
from src.cleaning import clean_instagram_data
from src.transformation import engineer_features, safe_divide
from src.database import get_db_connection, store_cleaned_data_to_db, load_from_db


class TestInstagramAnalyticsPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.raw_df = load_raw_dataset()

    def test_raw_ingestion(self):
        """Verify that the raw CSV loads with the expected dimensions and schema."""
        self.assertGreater(len(self.raw_df), 29000, "Dataset should have ~30,000 rows.")
        self.assertEqual(self.raw_df.shape[1], 23, "Raw dataset must contain 23 original columns.")
        self.assertIn("post_id", self.raw_df.columns)
        self.assertIn("account_id", self.raw_df.columns)

    def test_data_quality_assessment(self):
        """Verify that quality assessment completes and produces structured reports."""
        report = assess_data_quality(self.raw_df)
        self.assertIn("status", report)
        self.assertEqual(report["total_missing_values"], 0, "No null values should be present.")
        self.assertEqual(report["duplicate_rows"], 0, "No duplicate rows should exist.")
        self.assertEqual(report["duplicate_post_ids"], 0, "All post_ids must be strictly unique.")

    def test_cleaning_and_audit(self):
        """Verify cleaning rules and ensure legitimate records are not pruned."""
        cleaned_df, audit = clean_instagram_data(self.raw_df)
        self.assertEqual(len(cleaned_df), len(self.raw_df), "No legitimate records should be deleted.")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned_df["post_datetime"]))
        self.assertIn("post_hour", cleaned_df.columns)

    def test_feature_engineering(self):
        """Verify feature engineering calculations and non-zero logic."""
        cleaned_df, _ = clean_instagram_data(self.raw_df)
        transformed_df = engineer_features(cleaned_df)

        # Check total interactions
        expected_ints = transformed_df["likes"] + transformed_df["comments"] + transformed_df["shares"] + transformed_df["saves"]
        pd.testing.assert_series_equal(transformed_df["total_interactions"], expected_ints, check_names=False)

        # Check calculated engagement rate
        self.assertIn("calculated_engagement_rate", transformed_df.columns)
        self.assertTrue((transformed_df["calculated_engagement_rate"] >= 0).all())

        # Check hashtag grouping
        self.assertIn("hashtag_count_group", transformed_df.columns)
        self.assertIn("follower_count_group", transformed_df.columns)

    def test_database_persistence(self):
        """Verify SQLite table creation and record retrieval."""
        cleaned_df, _ = clean_instagram_data(self.raw_df)
        transformed_df = engineer_features(cleaned_df)

        test_db = Path("database/test_instagram.db")
        store_cleaned_data_to_db(transformed_df, db_path=test_db)
        
        # Query back
        res = load_from_db("SELECT COUNT(*) AS total FROM instagram_posts", db_path=test_db)
        self.assertEqual(int(res["total"].iloc[0]), len(transformed_df))
        
        # Clean up test db
        if test_db.exists():
            test_db.unlink()


if __name__ == "__main__":
    unittest.main()

