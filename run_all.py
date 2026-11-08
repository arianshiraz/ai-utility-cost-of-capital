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
          "10_ratecase_second_pass.py", "11_rate_base_proxy.py",
          "12_returns.py", "13_placebo_exposure.py", "14_h1_comovement.py", "15_h2_decomposition.py",
          "17_h3_replicas.py", "18_h3_us_panel.py", "19_h3_robustness.py",
          "09_build_workbook.py"]
if not os.environ.get("SEC_USER_AGENT"):
    print("SEC_USER_AGENT not set: skipping SEC stages 02, 03, 07, 10 and 13 (existing tables are reused)")
    stages = [s for s in stages if not s.startswith(("02_", "03_", "07_", "10_", "13_"))]
for script in stages:
    if script.endswith(".R"):
        continue
    print(f"== {script}")
    runpy.run_path(str(CODE / script), run_name="__main__")

# Figures: R script, run after the Python stages
import subprocess
rscript = os.environ.get("RSCRIPT", "Rscript")
subprocess.run([rscript, str(CODE / "16_figures.R")], check=True, cwd=ROOT)
