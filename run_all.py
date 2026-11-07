"""Rebuild every table and figure: python run_all.py (from the repository root).

Figures (later stages) need R (>= 4.3) with tidyplots, ggdist, distributional, dplyr, readr.
Set RSCRIPT to the Rscript path if it is not on PATH.
"""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
sys.path.insert(0, str(CODE))

import os

# Stages 02 and 03 query SEC EDGAR, which requires a contact in the User-Agent header:
# set the environment variable SEC_USER_AGENT (for example "Your Name your@email").
stages = ["01_download_prices.py", "02_collect_dc_disclosures.py", "03_dc_exposure_measures.py",
          "05_download_rates.py", "06_select_ratecase_units.py",
          "07_extract_ratecase_sentences.py", "08_ratecase_candidates.py",
          "10_ratecase_second_pass.py",
          "09_build_workbook.py"]
if not os.environ.get("SEC_USER_AGENT"):
    print("SEC_USER_AGENT not set: skipping SEC stages 02, 03, 07 and 10 (existing tables are reused)")
    stages = [s for s in stages if not s.startswith(("02_", "03_", "07_", "10_"))]
for script in stages:
    print(f"== {script}")
    runpy.run_path(str(CODE / script), run_name="__main__")
