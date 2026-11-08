"""H2: decomposition of regulator-style betas (docs/prespecification.md section 3; docs/analysis_notes.md).

For each utility, beta is estimated in each country's regulator window and frequency, ending
29 November 2022 (a) and 31 October 2026 (b). With m the local index return, m_AI the fitted value
of m on the raw local-currency SMH return, C = cov(u, m), C_ai = cov(u, m_AI), C_o = cov(u, m - m_AI)
and V = var(m):
    beta_b - beta_a = dC_ai / V_b  +  dC_o / V_b  +  C_a (1/V_b - 1/V_a)
                      exposure       non-AI          composition
Regulators do not drop the COVID months, so neither does this replica-style calculation.
Outputs in output/tables/: h2_decomposition.csv, h2_country.csv, h2_tests.csv.
"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from config import DERIVED, TABLES

_s = importlib.util.spec_from_file_location("h1", Path(__file__).with_name("14_h1_comovement.py"))
h1 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(h1)

END_A, END_B = pd.Timestamp("2022-11-29"), pd.Timestamp("2026-10-31")
WINDOWS = {  # country: [(years, frequency, main)]
    "US": [(5, "weekly", True)],
    "UK": [(10, "daily", True), (5, "daily", False), (2, "daily", False)],
    "DE": [(1, "daily", True), (3, "daily", False), (5, "daily", False)],
    "ES": [(6, "weekly", True)],
    "IT": [(5, "daily", True)],
    "CA": [(5, "weekly", False)],  # descriptive: no beta enters Canada's formula
}


def moments(w):
    m, s, u = w.m.values, w.smh.values, w.r.values
    X = np.column_stack([np.ones(len(m)), s])
    b, *_ = np.linalg.lstsq(X, m, rcond=None)
    m_ai = X @ b
    cov = lambda a, c: np.cov(a, c, ddof=1)[0, 1]
    V = np.var(m, ddof=1)
    return {"C": cov(u, m), "C_ai": cov(u, m_ai), "C_o": cov(u, m - m_ai), "V": V,
            "ai_share": 1 - np.var(m - m_ai, ddof=1) / V, "n": len(m)}


def main() -> None:
    data = {"daily": pd.read_parquet(DERIVED / "returns_daily.parquet"),
            "weekly": pd.read_parquet(DERIVED / "returns_weekly.parquet")}
    rows = []
    for c, specs in WINDOWS.items():
        for yrs, freq, main_w in specs:
            d = data[freq][data[freq].country == c]
            for t, df in d.groupby("ticker"):
                res = {}
                for tag, end in (("a", END_A), ("b", END_B)):
                    start = end - pd.DateOffset(years=yrs)
                    if t == "EVRG":
                        start = max(start, h1.EVRG_START)
                    w = df[(df.date > start) & (df.date <= end)]
                    if len(w) < (40 if freq == "weekly" else 150):
                        res = None
                        break
                    res[tag] = moments(w)
                if res is None:
                    continue
                a, b = res["a"], res["b"]
                beta_a, beta_b = a["C"] / a["V"], b["C"] / b["V"]
                exp_t = (b["C_ai"] - a["C_ai"]) / b["V"]
                oth_t = (b["C_o"] - a["C_o"]) / b["V"]
                comp_t = a["C"] * (1 / b["V"] - 1 / a["V"])
                assert abs(beta_b - beta_a - (exp_t + oth_t + comp_t)) < 1e-10
                rows.append({"ticker": t, "country": c, "role": df.role.iloc[0], "window_years": yrs,
                             "frequency": freq, "main_window": main_w, "beta_a": beta_a, "beta_b": beta_b,
                             "d_beta": beta_b - beta_a, "exposure_term": exp_t, "non_ai_term": oth_t,
                             "composition_term": comp_t, "ai_share_a": a["ai_share"], "ai_share_b": b["ai_share"],
                             "n_a": a["n"], "n_b": b["n"]})
    dec = pd.DataFrame(rows)
    dec.to_csv(TABLES / "h2_decomposition.csv", index=False, float_format="%.5f")
    el = dec[(dec.role == "regulated_electric")]
    country = (el.groupby(["country", "window_years", "frequency", "main_window"])
                 [["beta_a", "beta_b", "d_beta", "exposure_term", "non_ai_term", "composition_term",
                   "ai_share_a", "ai_share_b"]].mean().reset_index())
    country["n_utilities"] = el.groupby(["country", "window_years"]).size().values
    country["d_ai_share"] = country.ai_share_b - country.ai_share_a
    country.to_csv(TABLES / "h2_country.csv", index=False, float_format="%.5f")

    # tests on the main windows
    ex = pd.read_csv(TABLES / "dc_exposure_candidates.csv")
    e23 = ex[ex.vintage == "FY2023"][["ticker", "mentions_per_10k"]]
    hub = pd.read_csv(TABLES.parent.parent / "data" / "classification" / "hub_flags_nonus.csv")[["ticker", "hub_flag"]]
    mainw = dec[dec.main_window | (dec.country == "CA")]
    tests = []
    us = mainw[(mainw.country == "US") & (mainw.role == "regulated_electric")].merge(e23, on="ticker")
    b, se = h1.hc1(np.column_stack([np.ones(len(us)), us.mentions_per_10k]), us.exposure_term.values)
    tests.append({"test": "1 US: exposure term on FY2023 mentions per 10k (HC1)", "slope": b[1], "se": se[1],
                  "t": b[1] / se[1], "n": len(us)})
    allc = mainw[mainw.role == "regulated_electric"].merge(e23, on="ticker", how="left").merge(hub, on="ticker", how="left")
    allc["expo_raw"] = np.where(allc.country == "US", allc.mentions_per_10k, allc.hub_flag)
    allc["expo_z"] = allc.groupby("country").expo_raw.transform(lambda s: (s - s.mean()) / s.std() if s.std() > 0 else s * 0)
    D = pd.get_dummies(allc.country, drop_first=True).astype(float)
    coef, t0, p = h1.webb_boot(np.column_stack([np.ones(len(allc)), allc.expo_z, D.values]),
                               allc.exposure_term.values, allc.country.values, 1)
    tests.append({"test": "1 all countries: exposure term on within-country z exposure, country FE (wild cluster bootstrap p)",
                  "slope": coef, "t": t0, "p_boot": p, "n": len(allc)})
    cm = country[country.main_window | (country.country == "CA")]
    r = np.corrcoef(cm.composition_term, cm.d_ai_share)[0, 1]
    sl = np.polyfit(cm.d_ai_share, cm.composition_term, 1)[0]
    tests.append({"test": "2 countries: composition term against change in index AI share (correlation; slope)",
                  "slope": sl, "corr": r, "n": len(cm)})
    for _, rr in cm.iterrows():
        tests.append({"test": f"3 net change in beta, {rr.country} ({rr.window_years}y {rr.frequency})",
                      "slope": rr.d_beta, "n": rr.n_utilities})
    out = pd.DataFrame(tests)
    out.to_csv(TABLES / "h2_tests.csv", index=False, float_format="%.5f")
    pd.set_option("display.width", 220)
    print(country.round(3).to_string(index=False))
    print(out.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
