import contextlib
import io
import os
import sys
import unittest
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
MPL_CONFIG_DIR = REPO_ROOT / ".matplotlib-test"
MPL_CONFIG_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from NBA_전처리_모듈 import NBADataPreprocessor
from NBA_머신러닝_모듈 import NBAMachineLearning


class TestNBADataPreprocessor(unittest.TestCase):
    def test_convert_min_to_float_handles_expected_inputs(self):
        self.assertAlmostEqual(NBADataPreprocessor.convert_min_to_float("35:30"), 35.5)
        self.assertEqual(NBADataPreprocessor.convert_min_to_float("12"), 12.0)
        self.assertTrue(pd.isna(NBADataPreprocessor.convert_min_to_float("")))
        self.assertTrue(pd.isna(NBADataPreprocessor.convert_min_to_float("bad-value")))


class TestNBAMachineLearningSmoke(unittest.TestCase):
    def test_prepare_game_level_data_creates_binary_win_labels(self):
        ml = NBAMachineLearning()
        ml.df = pd.DataFrame(
            [
                {
                    "GAME_ID": 1,
                    "TEAM_ID": 10,
                    "HOME_TEAM_ID": 10,
                    "VISITOR_TEAM_ID": 20,
                    "SEASON": "2023-24",
                    "GAME_DATE_EST": pd.Timestamp("2024-01-01"),
                    "PTS": 110,
                    "AST": 25,
                    "REB": 40,
                    "FG_PCT": 0.48,
                    "FG3_PCT": 0.37,
                    "FT_PCT": 0.82,
                    "STL": 8,
                    "BLK": 4,
                    "TO": 11,
                    "PF": 18,
                    "FGM": 42,
                    "FGA": 88,
                    "FG3M": 12,
                    "FG3A": 32,
                    "EFG_PCT": 0.55,
                    "TS_PCT": 0.59,
                    "SEI": 1.1,
                    "PPM": 0.95,
                    "PLUS_MINUS": 6,
                },
                {
                    "GAME_ID": 1,
                    "TEAM_ID": 10,
                    "HOME_TEAM_ID": 10,
                    "VISITOR_TEAM_ID": 20,
                    "SEASON": "2023-24",
                    "GAME_DATE_EST": pd.Timestamp("2024-01-01"),
                    "PTS": 108,
                    "AST": 23,
                    "REB": 39,
                    "FG_PCT": 0.47,
                    "FG3_PCT": 0.35,
                    "FT_PCT": 0.81,
                    "STL": 7,
                    "BLK": 5,
                    "TO": 10,
                    "PF": 17,
                    "FGM": 41,
                    "FGA": 87,
                    "FG3M": 11,
                    "FG3A": 31,
                    "EFG_PCT": 0.54,
                    "TS_PCT": 0.58,
                    "SEI": 1.0,
                    "PPM": 0.93,
                    "PLUS_MINUS": 5,
                },
                {
                    "GAME_ID": 2,
                    "TEAM_ID": 30,
                    "HOME_TEAM_ID": 30,
                    "VISITOR_TEAM_ID": 40,
                    "SEASON": "2023-24",
                    "GAME_DATE_EST": pd.Timestamp("2024-01-03"),
                    "PTS": 94,
                    "AST": 19,
                    "REB": 35,
                    "FG_PCT": 0.41,
                    "FG3_PCT": 0.29,
                    "FT_PCT": 0.74,
                    "STL": 5,
                    "BLK": 3,
                    "TO": 14,
                    "PF": 20,
                    "FGM": 35,
                    "FGA": 85,
                    "FG3M": 8,
                    "FG3A": 28,
                    "EFG_PCT": 0.47,
                    "TS_PCT": 0.5,
                    "SEI": 0.8,
                    "PPM": 0.79,
                    "PLUS_MINUS": -4,
                },
                {
                    "GAME_ID": 2,
                    "TEAM_ID": 30,
                    "HOME_TEAM_ID": 30,
                    "VISITOR_TEAM_ID": 40,
                    "SEASON": "2023-24",
                    "GAME_DATE_EST": pd.Timestamp("2024-01-03"),
                    "PTS": 96,
                    "AST": 20,
                    "REB": 34,
                    "FG_PCT": 0.42,
                    "FG3_PCT": 0.3,
                    "FT_PCT": 0.75,
                    "STL": 6,
                    "BLK": 2,
                    "TO": 15,
                    "PF": 21,
                    "FGM": 36,
                    "FGA": 86,
                    "FG3M": 9,
                    "FG3A": 29,
                    "EFG_PCT": 0.48,
                    "TS_PCT": 0.51,
                    "SEI": 0.82,
                    "PPM": 0.8,
                    "PLUS_MINUS": -3,
                },
            ]
        )

        with contextlib.redirect_stdout(io.StringIO()):
            game_stats = ml.prepare_game_level_data()

        self.assertEqual(len(game_stats), 2)
        self.assertEqual(set(game_stats["WIN"].tolist()), {0, 1})
        self.assertTrue({"GAME_ID", "WIN", "PLUS_MINUS"}.issubset(game_stats.columns))

    def test_prepare_player_performance_data_adds_lag_features(self):
        ml = NBAMachineLearning()
        ml.df = pd.DataFrame(
            [
                {
                    "PLAYER_NAME": "Player A",
                    "MIN": 400,
                    "GAME_DATE_EST": pd.Timestamp("2024-01-01"),
                    "PTS": 20,
                    "AST": 5,
                    "REB": 7,
                    "FG_PCT": 0.5,
                    "STL": 2,
                    "BLK": 1,
                    "TO": 3,
                    "PLUS_MINUS": 8,
                },
                {
                    "PLAYER_NAME": "Player A",
                    "MIN": 350,
                    "GAME_DATE_EST": pd.Timestamp("2024-01-03"),
                    "PTS": 18,
                    "AST": 6,
                    "REB": 8,
                    "FG_PCT": 0.46,
                    "STL": 1,
                    "BLK": 1,
                    "TO": 2,
                    "PLUS_MINUS": 4,
                },
                {
                    "PLAYER_NAME": "Player A",
                    "MIN": 300,
                    "GAME_DATE_EST": pd.Timestamp("2024-01-05"),
                    "PTS": 24,
                    "AST": 7,
                    "REB": 9,
                    "FG_PCT": 0.52,
                    "STL": 3,
                    "BLK": 2,
                    "TO": 4,
                    "PLUS_MINUS": 10,
                },
                {
                    "PLAYER_NAME": "Player B",
                    "MIN": 120,
                    "GAME_DATE_EST": pd.Timestamp("2024-01-02"),
                    "PTS": 9,
                    "AST": 2,
                    "REB": 4,
                    "FG_PCT": 0.4,
                    "STL": 1,
                    "BLK": 0,
                    "TO": 1,
                    "PLUS_MINUS": -2,
                },
            ]
        )

        with contextlib.redirect_stdout(io.StringIO()):
            player_df = ml.prepare_player_performance_data()

        self.assertEqual(player_df["PLAYER_NAME"].nunique(), 1)
        self.assertEqual(player_df["PLAYER_NAME"].iloc[0], "Player A")
        self.assertIn("PTS_LAG5", player_df.columns)
        self.assertIn("PLUS_MINUS_LAG5", player_df.columns)
        self.assertFalse(player_df["PTS_LAG5"].isna().any())


if __name__ == "__main__":
    unittest.main()
