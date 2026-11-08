"""H3 robustness checks (docs/prespecification.md section 6; docs/analysis_notes.md, the entry on
which checks apply to H3). Each check reruns the replicas and the US panel through the same code
with one setting changed; all report the "both" counterfactual.
Output: output/tables/h3_robustness.csv
"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from config import TABLES


def _load(name, file):
    s = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


rep = _load("rep", "17_h3_replicas.py")
us = _load("us", "18_h3_us_panel.py")
CHECKS = {
    "main": {},
    "1 NVDA instead of SMH": {"ai": "nvda"},
    "2 USD-based": {"usd": True},
    "4 AI era from 1 January 2024": {"ai_date": pd.Timestamp("2024-01-01"), "post": ("2024-01-01", "2026-10-31")},
    "7 National Grid half US, half UK": {"ng_blend": True},
}


def set_cfg(over):
    for mod in (rep, us.rep):
        mod.CFG.update({"ai": "smh", "ai_date": rep.AI_DATE, "post": rep.h1.POST, "usd": False, "ng_blend": False,
                        "write": False})
        mod.CFG.update(over)


def main() -> None:
    rows = []
    for name, over in CHECKS.items():
        set_cfg(over)
        s, t = rep.uk()
        b = s[s.counterfactual == "both"].iloc[0]
        rows.append({"check": name, "determination": "UK RIIO-3", "bps": b.bps, "d_beta": b.d_asset_beta,
                     "detail": f"implied gearing {t.implied_gearing.min():.2f} to {t.implied_gearing.max():.2f}"})
        if name.startswith("7"):
            continue  # National Grid check applies to the UK replica only
        s, _ = rep.de()
        for _, r in s[s.counterfactual == "both"].iterrows():
            rows.append({"check": name, "determination": f"Germany, prospective, {r.window_years}y", "bps": r.bps,
                         "d_beta": r.d_asset_beta, "detail": f"{r.n_comparators_used} comparators pass the gearing check"})
        s, _ = rep.es()
        b = s[s.counterfactual == "both"].iloc[0]
        rows.append({"check": name, "determination": "Spain 2026-2031", "bps": b.bps, "d_beta": b.d_relevered_beta, "detail": ""})
        if name.startswith("2"):
            continue  # US units are already in dollars
        R, D = us.main(write=False)
        for _, r in R.iterrows():
            rows.append({"check": name, "determination": f"US panel, {r.spec}", "bps": np.nan, "d_beta": np.nan,
                         "coef": r.coef_d_c, "se": r.se, "p_boot": r.p_boot, "n_pairs": r.n_pairs,
                         "median_c_ai_era": D[D.date >= "2023-01-01"].c.median()})
    set_cfg({})
    R, D = us.main(exclude=("EIX", "PCG"), write=False)
    for _, r in R.iterrows():
        rows.append({"check": "3 excluding EIX and PCG", "determination": f"US panel, {r.spec}", "bps": np.nan,
                     "d_beta": np.nan, "coef": r.coef_d_c, "se": r.se, "p_boot": r.p_boot, "n_pairs": r.n_pairs,
                     "median_c_ai_era": D[D.date >= "2023-01-01"].c.median()})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "h3_robustness.csv", index=False, float_format="%.5f")
    pd.set_option("display.width", 240)
    print(out.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
