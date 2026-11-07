"""Shared settings for the utility cost-of-capital project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
UTILITIES = ROOT / "data" / "classification" / "utilities.csv"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"

# Long history: regulators typically estimate betas over 2 to 5 years, and the pre-AI
# baseline needs several years before November 2022.
START = "2012-01-01"
END = "2026-11-07"

# Market index per country (local currency) and the AI factor candidates (USD).
# Pre-specification, section 1: the broadest local index available. UK: FTSE All-Share (^FTAS).
# Germany: CDAX is not on Yahoo Finance, so the DAX is used (substitution recorded 7 Nov 2026).
MARKET_INDEX = {"US": "^GSPC", "UK": "^FTAS", "DE": "^GDAXI", "ES": "^IBEX",
                "IT": "FTSEMIB.MI", "CA": "^GSPTSE", "AU": "^AXJO", "JP": "^N225"}
AI_FACTORS = ["SMH", "NVDA"]
# Kept for comparison with the earlier download: FTSE 100.
EXTRA_SERIES = ["^FTSE"]
FX = {"UK": "GBPUSD=X", "DE": "EURUSD=X", "ES": "EURUSD=X", "IT": "EURUSD=X",
      "CA": "CADUSD=X", "AU": "AUDUSD=X", "JP": "JPYUSD=X"}

# Decision D1 (7 Nov 2026): countries used in hypothesis tests. AU and JP are descriptive only.
CORE_COUNTRIES = ["US", "UK", "DE", "ES", "IT", "CA"]

# Start of the "AI era" for before/after comparisons: public release of ChatGPT.
AI_ERA_START = "2022-11-30"
