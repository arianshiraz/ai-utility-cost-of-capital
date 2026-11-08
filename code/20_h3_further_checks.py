"""Further H3 checks written down on 8 November 2026 before they ran (docs/analysis_notes.md, last entry):
1. a composition counterfactual that holds the AI factor's share of index variance (R²) at its pre-AI value,
   with the index moments behind the slope;
2. month-block bootstrap intervals and placebo-break ranks for each replica contribution;
3. how much of the US regressor is explained by the timing of the decision.
The replica functions in 17_h3_replicas.py are run once to collect each comparator's returns, gearing and
window; a lean re-implementation then reproduces their contributions exactly (checked below) and reruns them.
Outputs in output/tables/: h3_further_moments.csv, h3_further_alt_counterfactual.csv,
h3_further_uncertainty.csv, h3_further_placebo_draws.csv, h3_further_us_timing.csv.
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
h1 = rep.h1
AI_DATE = rep.AI_DATE
COV0, COV1 = np.datetime64(h1.COVID[0]), np.datetime64(h1.COVID[1])
NB = 1000  # bootstrap draws (placebo breaks: h1.NDRAW, same seed as H1)
US_ORIG = (us.rep.loadings, us.rep.counterfactual)


# ---------- collect comparator data from the replica functions ----------
def collect(fn):
    got, orig = [], rep.loadings
    rep.loadings = lambda df: (got.append(df.copy()), orig(df))[1]
    try:
        s, t = fn()
    finally:
        rep.loadings = orig
    return s, t, got


def prep(df, f="smh"):
    return {"date": df.date.values.astype("datetime64[D]"), "r": df.r.values.astype(float),
            "m": df.m.values.astype(float), "f": df[f].values.astype(float), "dy": df.dy.values.astype(float)}


def period_rows(a, lo, hi):
    d = a["date"]
    return np.flatnonzero((d >= np.datetime64(lo, "D")) & (d <= np.datetime64(hi, "D")) & ~((d >= COV0) & (d <= COV1)))


def est(a, idx):
    """Loadings on rows idx, as in rep.loadings, plus the moments the R² counterfactual needs."""
    m, f, r, dy = a["m"][idx], a["f"][idx], a["r"][idx], a["dy"][idx]
    one = np.ones(len(idx))
    k, perp = h1.ols(np.column_stack([one, m]), f)
    bb, _ = h1.ols(np.column_stack([one, m, perp, dy]), r)
    g, u = h1.ols(np.column_stack([one, f]), m)
    return {"b_ai": bb[2], "g": g[1], "orth": k, "var_f": f.var(), "var_u": u.var(), "r2": 1 - u.var() / m.var(),
            "cov_mf": np.cov(m, f)[0, 1], "var_m": m.var()}


def g_target(L, target):
    if target == "slope":
        return L["pre"]["g"]
    r2 = L["pre"]["r2"]
    return np.sign(L["pre"]["g"]) * np.sqrt(r2 * L["ai"]["var_u"] / ((1 - r2) * L["ai"]["var_f"]))


def slope(y, x):
    x = x - x.mean()
    return float((x * (y - y.mean())).sum() / (x ** 2).sum())


def delta(a, L, cf_lo, cf_hi, w_lo, w_hi, target):
    """Actual minus counterfactual equity beta ('both') in the window [w_lo, w_hi]; all days kept."""
    d = a["date"]
    w = (d >= np.datetime64(w_lo, "D")) & (d <= np.datetime64(w_hi, "D"))
    mask = (d >= np.datetime64(cf_lo, "D")) & (d <= np.datetime64(cf_hi, "D"))
    k = L["ai"]["orth"]
    perp = a["f"] - (k[0] + k[1] * a["m"])
    r_cf = np.where(mask, a["r"] - (L["ai"]["b_ai"] - L["pre"]["b_ai"]) * perp, a["r"])
    m_cf = np.where(mask, a["m"] - (L["ai"]["g"] - g_target(L, target)) * a["f"], a["m"])
    return slope(a["r"][w], a["m"][w]) - slope(r_cf[w], m_cf[w])


# ---------- determinations ----------
def build():
    rep.CFG["write"] = False
    s_uk, t_uk, d_uk = collect(rep.uk)
    s_de, t_de, d_de = collect(rep.de)
    s_es, t_es, d_es = collect(rep.es)
    uk_idx = {"UK": "FTSE All-Share", "ES": "IBEX 35", "IT": "FTSE MIB"}
    D = [{"name": "UK RIIO-3", "firms": [prep(x) for x in d_uk], "index": [uk_idx[c] for c in t_uk.country],
          "end": pd.Timestamp("2025-03-31"), "years": 10, "w": np.ones(len(t_uk)),
          "lev": (1 - t_uk.implied_gearing.values), "scale": 0.046 / 0.45 * 1e4,
          "main": float(s_uk.loc[s_uk.counterfactual == "both", "bps"].iloc[0])}]
    for yrs in (1, 3, 5):
        g = t_de[f"implied_gearing_{yrs}y"].values
        ok = ((g >= 0.2) & (g <= 0.75)).astype(float)
        D.append({"name": f"Germany, prospective, {yrs}y", "firms": [prep(x) for x in d_de], "index": list(t_de["index"]),
                  "end": pd.Timestamp("2026-10-31"), "years": yrs, "w": ok, "lev": 1 - g, "scale": 0.037 / 0.40 * 1e4,
                  "main": float(s_de[(s_de.window_years == yrs) & (s_de.counterfactual == "both")].bps.iloc[0])})
    relever = 1 + (1 - 0.25) * 0.85
    D.append({"name": "Spain 2026-2031", "firms": [prep(x) for x in d_es], "index": list(t_es["index"]),
              "end": pd.Timestamp("2023-12-31"), "start": pd.Timestamp("2018-01-01"), "years": 6,
              "w": np.ones(len(t_es)), "lev": 1 / (1 + (1 - t_es.tax.values) * t_es.cnmc_de.values),
              "scale": relever * 0.0498 * 1e4,
              "main": float(s_es.loc[s_es.counterfactual == "both", "bps"].iloc[0])})
    for x in D:
        x.setdefault("start", x["end"] - pd.DateOffset(years=x["years"]))
    return D


def bps(x, Ls, cf_lo, cf_hi, w_lo, w_hi, target):
    vals = np.array([delta(a, L, cf_lo, cf_hi, w_lo, w_hi, target) if L is not None else np.nan
                     for a, L in zip(x["firms"], Ls)])
    use = (x["w"] > 0) & ~np.isnan(vals)
    return float(np.mean(x["lev"][use] * vals[use]) * x["scale"])


def main_loadings(x, pre=h1.PRE, post=h1.POST):
    return [{"pre": est(a, period_rows(a, *pre)), "ai": est(a, period_rows(a, *post))} for a in x["firms"]]


def check1(D):
    rows, mom = [], []
    for x in D:
        Ls = main_loadings(x)
        x["L"] = Ls
        b_slope = bps(x, Ls, AI_DATE, "2100-01-01", x["start"], x["end"], "slope")
        assert abs(b_slope - x["main"]) < 1e-6, (x["name"], b_slope, x["main"])  # lean code reproduces 17_h3_replicas
        rows.append({"determination": x["name"], "bps_main_slope_held": b_slope,
                     "bps_variance_share_held": bps(x, Ls, AI_DATE, "2100-01-01", x["start"], x["end"], "r2")})
        seen = set()
        for i, L in zip(x["index"], Ls):
            if i in seen:
                continue
            seen.add(i)
            mom.append({"determination": x["name"], "index": i,
                        **{f"{k}_{p}": L[p][k] for p in ("pre", "ai") for k in ("var_f", "cov_mf", "var_m", "g", "r2")},
                        "g_target_r2": g_target(L, "r2")})
    # US: the S&P 500 moments and the panel under the variance-share counterfactual
    wk = pd.read_parquet(rep.DERIVED / "returns_weekly.parquet")
    a = prep(wk[wk.ticker == wk[wk.country == "US"].ticker.iloc[0]].sort_values("date"))
    L = {"pre": est(a, period_rows(a, *h1.PRE)), "ai": est(a, period_rows(a, *h1.POST))}
    mom.append({"determination": "US rate cases (weekly)", "index": "S&P 500",
                **{f"{k}_{p}": L[p][k] for p in ("pre", "ai") for k in ("var_f", "cov_mf", "var_m", "g", "r2")},
                "g_target_r2": g_target(L, "r2")})
    us_rows = []
    for target in ("slope", "r2"):
        us.rep.loadings = lambda df: (lambda a: {"pre": est(a, period_rows(a, *h1.PRE)),
                                                 "ai": est(a, period_rows(a, *h1.POST))})(prep(df))

        def cf(df, L, which, target=target):
            a = prep(df)
            d = df.copy()
            mask = df.date.values >= np.datetime64(AI_DATE)
            k = L["ai"]["orth"]
            perp = a["f"] - (k[0] + k[1] * a["m"])
            d["r_cf"] = np.where(mask & (which in ("exposure", "both")), a["r"] - (L["ai"]["b_ai"] - L["pre"]["b_ai"]) * perp, a["r"])
            d["m_cf"] = np.where(mask & (which in ("composition", "both")), a["m"] - (L["ai"]["g"] - g_target(L, target)) * a["f"], a["m"])
            return d
        us.rep.counterfactual = cf
        R, Dd = us.main(write=False)
        for _, r in R.iterrows():
            us_rows.append({"determination": f"US panel, {r.spec}", "counterfactual": target, "coef": r.coef_d_c,
                            "se": r.se, "p_boot": r.p_boot,
                            "median_c_ai_era": Dd[Dd.date >= "2023-01-01"].c.median()})
    main_us = pd.read_csv(TABLES / "h3_us_panel.csv")
    chk = [u for u in us_rows if u["counterfactual"] == "slope" and u["determination"].endswith("(pre-specified)")][0]
    assert abs(chk["coef"] - main_us.loc[main_us.spec.str.startswith("state"), "coef_d_c"].iloc[0]) < 1e-4  # table rounded to 5 decimals
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "h3_further_alt_counterfactual.csv", index=False, float_format="%.5f")
    pd.DataFrame(us_rows).to_csv(TABLES / "h3_further_alt_counterfactual_us.csv", index=False, float_format="%.5f")
    pd.DataFrame(mom).to_csv(TABLES / "h3_further_moments.csv", index=False, float_format="%.7f")
    print(out.round(3).to_string(index=False))
    print(pd.DataFrame(us_rows).round(4).to_string(index=False))
    print(pd.DataFrame(mom)[["determination", "index", "var_f_pre", "var_f_ai", "cov_mf_pre", "cov_mf_ai",
                              "g_pre", "g_ai", "r2_pre", "r2_ai", "g_target_r2"]].round(6).to_string(index=False))


def check2(D):
    # (a) month-block bootstrap of the loadings
    rng = np.random.default_rng(h1.SEED)
    months = {p: pd.period_range(lo, hi, freq="M") for p, (lo, hi) in (("pre", h1.PRE), ("ai", h1.POST))}
    for x in D:
        x["by_month"] = []
        for a in x["firms"]:
            mo = a["date"].astype("datetime64[M]")
            x["by_month"].append({p: {m: np.intersect1d(np.flatnonzero(mo == np.datetime64(str(m), "M")),
                                                         period_rows(a, *(h1.PRE if p == "pre" else h1.POST)))
                                      for m in months[p]} for p in ("pre", "ai")})
    boot = {(x["name"], t): [] for x in D for t in ("slope", "r2")}
    for _ in range(NB):
        draw = {p: rng.choice(len(months[p]), len(months[p]), replace=True) for p in months}
        for x in D:
            Ls = []
            for a, bm in zip(x["firms"], x["by_month"]):
                L = {}
                for p in ("pre", "ai"):
                    idx = np.concatenate([bm[p][months[p][j]] for j in draw[p]])
                    L[p] = est(a, idx)
                Ls.append(L)
            for t in ("slope", "r2"):
                boot[(x["name"], t)].append(bps(x, Ls, AI_DATE, "2100-01-01", x["start"], x["end"], t))
    # (b) placebo breaks, as in H1
    prng = np.random.default_rng(h1.SEED)
    lo, hi = pd.Timestamp("2015-01-01"), pd.Timestamp("2021-12-31")
    breaks = lo + pd.to_timedelta(prng.integers(0, (hi - lo).days + 1, h1.NDRAW), unit="D")
    draws = []
    for B in breaks:
        pre = (max(B - h1.LPRE, h1.DATA_START), B)
        post = (B + pd.Timedelta(days=h1.GAP_DAYS), min(B + pd.Timedelta(days=h1.GAP_DAYS) + h1.LPOST, h1.AI_START))
        for x in D:
            Ls = []
            for a in x["firms"]:
                ip, ia = period_rows(a, *pre), period_rows(a, *post)
                Ls.append({"pre": est(a, ip), "ai": est(a, ia)} if min(len(ip), len(ia)) >= 30 else None)
            end_p = min(B + (x["end"] - AI_DATE), h1.AI_START)
            start_p = end_p - (x["end"] - x["start"])
            eff_start = max(start_p, h1.DATA_START)
            share = (end_p - max(B, eff_start)) / (end_p - eff_start)
            for t in ("slope", "r2"):
                draws.append({"determination": x["name"], "counterfactual": t, "break": B.date(),
                              "bps": bps(x, Ls, B, end_p, start_p, end_p, t), "post_break_share_of_window": share})
    draws = pd.DataFrame(draws)
    draws.to_csv(TABLES / "h3_further_placebo_draws.csv", index=False, float_format="%.5f")
    rows = []
    for x in D:
        main_share = (x["end"] - max(AI_DATE, x["start"])) / (x["end"] - x["start"])
        for t in ("slope", "r2"):
            v = bps(x, x["L"], AI_DATE, "2100-01-01", x["start"], x["end"], t)
            b = np.array(boot[(x["name"], t)])
            p = draws[(draws.determination == x["name"]) & (draws.counterfactual == t)].dropna(subset=["bps"])
            # breaks without enough comparator data (Spanish prices start in June 2017) are dropped and counted
            rows.append({"determination": x["name"], "counterfactual": t, "bps": v,
                         "boot_p2_5": np.percentile(b, 2.5), "boot_p97_5": np.percentile(b, 97.5),
                         "boot_share_le_0": float((b <= 0).mean()),
                         "placebo_median": p.bps.median(), "placebo_p5": p.bps.quantile(0.05), "placebo_p95": p.bps.quantile(0.95),
                         "p_placebo_one_sided": float((p.bps >= v).mean()),
                         "p_placebo_two_sided": float((p.bps.abs() >= abs(v)).mean()),
                         "n_placebo": len(p), "post_share_main": main_share, "post_share_placebo_median": p.post_break_share_of_window.median()})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "h3_further_uncertainty.csv", index=False, float_format="%.5f")
    pd.set_option("display.width", 260)
    print(out.round(3).to_string(index=False))


def check3():
    us.rep.loadings, us.rep.counterfactual = US_ORIG  # back to the main versions
    R, D = us.main(write=False)
    D = D.copy()
    start = D.date - pd.DateOffset(years=5)
    D["share"] = ((D.date - AI_DATE).dt.days / (D.date - start).dt.days).clip(lower=0, upper=1)
    ai = D[D.date >= "2023-01-01"]
    X = np.column_stack([np.ones(len(ai)), ai.share])
    _, e = h1.ols(X, ai.c.values)
    r2_level = 1 - e.var() / ai.c.var(ddof=0)
    P = D.sort_values(["ticker", "date"]).copy()
    for col in ("roe", "c", "share", "t10", "baa"):
        P[f"d_{col}"] = P.groupby("ticker")[col].diff()
    P = P.dropna(subset=["d_roe"])
    X = np.column_stack([np.ones(len(P)), P.d_share])
    _, e = h1.ols(X, P.d_c.values)
    r2_diff = 1 - e.var() / P.d_c.var(ddof=0)
    cl = P.state.values
    SFE = pd.get_dummies(P.state, drop_first=True).astype(float).values
    YFE = pd.get_dummies(P.date.dt.year, drop_first=True).astype(float).values
    rows = []
    for label, var, fes in (("change in c, state FE (pre-specified)", "d_c", [SFE]),
                            ("change in c, no FE", "d_c", []),
                            ("change in AI-era window share, state FE", "d_share", [SFE]),
                            ("change in AI-era window share, no FE", "d_share", []),
                            ("change in c, state FE and decision-year FE", "d_c", [SFE, YFE]),
                            ("change in c, decision-year FE", "d_c", [YFE])):
        Xm = np.column_stack([np.ones(len(P)), P[var], P.d_t10, P.d_baa] + fes)
        keep = np.linalg.matrix_rank(Xm) == Xm.shape[1]
        if not keep:  # drop collinear dummy columns
            q, rr = np.linalg.qr(Xm)
            Xm = Xm[:, np.abs(np.diag(rr)) > 1e-10]
        b, se = us.cluster_se(Xm, P.d_roe.values, cl)
        _, t0, pb = h1.webb_boot(Xm, P.d_roe.values, cl, 1)
        rows.append({"specification": label, "coef": b[1], "se": se[1], "p_boot": pb, "n_pairs": len(P),
                     "r2_c_on_share_ai_decisions": r2_level, "r2_dc_on_dshare_pairs": r2_diff})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "h3_further_us_timing.csv", index=False, float_format="%.5f")
    print(out.round(4).to_string(index=False))


def slope_trend():
    """Descriptive, added after check 2 ran: how often the index's slope on SMH falls, and SMH's variance rises,
    between the pre and post periods of the H1 placebo breaks (S&P 500 and FTSE All-Share, daily)."""
    d = pd.read_parquet(rep.DERIVED / "returns_daily.parquet")
    prng = np.random.default_rng(h1.SEED)
    lo, hi = pd.Timestamp("2015-01-01"), pd.Timestamp("2021-12-31")
    breaks = lo + pd.to_timedelta(prng.integers(0, (hi - lo).days + 1, h1.NDRAW), unit="D")
    rows = []
    for tic, idx in (("AEP", "S&P 500"), ("NG.L", "FTSE All-Share")):
        a = prep(d[d.ticker == tic].sort_values("date"))
        n_fall = n_vup = 0
        for B in breaks:
            pre = (max(B - h1.LPRE, h1.DATA_START), B)
            post = (B + pd.Timedelta(days=h1.GAP_DAYS), min(B + pd.Timedelta(days=h1.GAP_DAYS) + h1.LPOST, h1.AI_START))
            e0, e1 = est(a, period_rows(a, *pre)), est(a, period_rows(a, *post))
            n_fall += e1["g"] < e0["g"]
            n_vup += e1["var_f"] > e0["var_f"]
        rows.append({"index": idx, "share_breaks_slope_falls": n_fall / len(breaks),
                     "share_breaks_smh_variance_rises": n_vup / len(breaks)})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "h3_further_slope_trend.csv", index=False, float_format="%.3f")
    print(out.to_string(index=False))


def us_cluster_by_utility():
    """Reporting addition (analysis notes, 8 November 2026): the US panel with clustering by utility as in the
    pre-specification, next to the state clustering used for the main results."""
    us.rep.loadings, us.rep.counterfactual = US_ORIG
    _, D = us.main(write=False)
    P = D.sort_values(["ticker", "date"]).copy()
    for col in ("roe", "c", "t10", "baa"):
        P[f"d_{col}"] = P.groupby("ticker")[col].diff()
    P = P.dropna(subset=["d_roe"])
    base = np.column_stack([np.ones(len(P)), P.d_c, P.d_t10, P.d_baa])
    FE = pd.get_dummies(P.state, drop_first=True).astype(float).values
    rows = []
    for spec, X in (("no fixed effects", base), ("state fixed effects (pre-specified)", np.column_stack([base, FE]))):
        for name, cl in (("state", P.state.values), ("utility", P.ticker.values)):
            b, se = us.cluster_se(X, P.d_roe.values, cl)
            _, _, pb = h1.webb_boot(X, P.d_roe.values, cl, 1)
            rows.append({"spec": spec, "cluster": name, "n_clusters": len(np.unique(cl)), "coef": b[1], "se": se[1],
                         "p_boot": pb})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "h3_further_us_clustering.csv", index=False, float_format="%.5f")
    print(out.round(4).to_string(index=False))


def uk_end_dates(D):
    """Reporting addition (analysis notes, 8 November 2026): the UK contribution for other window end dates."""
    x = [d for d in D if d["name"] == "UK RIIO-3"][0]
    Ls = main_loadings(x)
    rows = []
    for end in ("2024-12-31", "2025-03-31", "2025-09-30"):
        e = pd.Timestamp(end)
        st = e - pd.DateOffset(years=10)
        rows.append({"window_end": end, "bps_slope_held": bps(x, Ls, AI_DATE, "2100-01-01", st, e, "slope"),
                     "bps_variance_share_held": bps(x, Ls, AI_DATE, "2100-01-01", st, e, "r2")})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "h3_further_uk_end_dates.csv", index=False, float_format="%.5f")
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    D = build()
    check1(D)
    check2(D)
    check3()
    slope_trend()
    us_cluster_by_utility()
    uk_end_dates(D)
