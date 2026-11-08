"""H1: co-movement with AI stocks (docs/prespecification.md section 2; docs/analysis_notes.md).

For each utility: r = a + b_m m + b_ai ai_perp + b_r dy + e, estimated separately in the pre-AI and
AI-era windows, with the AI factor orthogonalised to the local index inside each window.
Outcome: change in b_ai and in the partial R-squared of the AI factor.
Tests: US cross-section of the change on FY2023 data-centre exposure (HC1); pooled placebo test;
all-country specification with within-country standardised exposure and country fixed effects
(wild cluster bootstrap by country, Webb weights); 1,000 placebo break dates; robustness checks.
Outputs in output/tables/: h1_utility_betas.csv, h1_tests.csv, h1_placebo_breaks.csv.
"""
import numpy as np
import pandas as pd

from config import DERIVED, TABLES

PRE = ("2017-01-01", "2022-11-29")
POST = ("2023-01-01", "2026-10-31")
COVID = ("2020-02-24", "2020-06-30")
GAP_DAYS = (pd.Timestamp(POST[0]) - pd.Timestamp(PRE[1])).days
LPRE = pd.Timestamp(PRE[1]) - pd.Timestamp(PRE[0])
LPOST = pd.Timestamp(POST[1]) - pd.Timestamp(POST[0])
DATA_START, AI_START = pd.Timestamp("2012-01-02"), pd.Timestamp("2022-11-29")
EVRG_START = pd.Timestamp("2019-06-04")
SEED, NDRAW = 20261108, 1000


def ols(X, y):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b, y - X @ b


def window_beta(df, start, end, ai="smh"):
    w = df[(df.date >= start) & (df.date <= end)]
    w = w[~((w.date >= COVID[0]) & (w.date <= COVID[1]))]
    if len(w) < 60:
        return None
    m, y = w.m.values, w.r.values
    one = np.ones(len(w))
    _, ai_perp = ols(np.column_stack([one, m]), w[ai].values)
    X = np.column_stack([one, m, ai_perp, w.dy.values])
    b, e = ols(X, y)
    _, e0 = ols(np.column_stack([one, m, w.dy.values]), y)
    sse, sse0 = (e ** 2).sum(), (e0 ** 2).sum()
    s2 = sse / (len(y) - 4)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return {"b_m": b[1], "b_ai": b[2], "se_ai": se[2], "b_r": b[3], "pr2_ai": (sse0 - sse) / sse0, "n": len(y)}


def utility_table(ret, pre=PRE, post=POST, ai="smh"):
    rows = []
    for t, df in ret.groupby("ticker"):
        p0 = pd.Timestamp(pre[0])
        if t == "EVRG":
            p0 = max(p0, EVRG_START)
        a = window_beta(df, p0, pd.Timestamp(pre[1]), ai)
        b = window_beta(df, pd.Timestamp(post[0]), pd.Timestamp(post[1]), ai)
        if a is None or b is None:
            continue
        rows.append({"ticker": t, "country": df.country.iloc[0], "role": df.role.iloc[0],
                     **{f"{k}_pre": v for k, v in a.items()}, **{f"{k}_post": v for k, v in b.items()}})
    u = pd.DataFrame(rows)
    u["d_b_ai"] = u.b_ai_post - u.b_ai_pre
    u["d_pr2_ai"] = u.pr2_ai_post - u.pr2_ai_pre
    return u


def hc1(X, y):
    b, e = ols(X, y)
    n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    V = XtXi @ (X.T * e ** 2) @ X @ XtXi * n / (n - k)
    return b, np.sqrt(np.diag(V))


def us_test(u, expo, outcome="d_b_ai", col="mentions_per_10k"):
    d = u[(u.country == "US") & (u.role == "regulated_electric")].merge(expo, on="ticker")
    X = np.column_stack([np.ones(len(d)), d[col].values])
    b, se = hc1(X, d[outcome].values)
    return {"slope": b[1], "se": se[1], "t": b[1] / se[1], "intercept": b[0], "n": len(d)}


def webb_boot(X, y, cl, j, B=9999, seed=SEED):
    """Wild cluster bootstrap p-value for coefficient j, null imposed, Webb six-point weights."""
    rng = np.random.default_rng(seed)
    b, e = ols(X, y)
    def tstat(Xm, yy):
        bb, ee = ols(Xm, yy)
        XtXi = np.linalg.inv(Xm.T @ Xm)
        meat = sum(np.outer(Xm[cl == g].T @ ee[cl == g], Xm[cl == g].T @ ee[cl == g]) for g in np.unique(cl))
        V = XtXi @ meat @ XtXi
        return bb[j] / np.sqrt(V[j, j])
    t0 = tstat(X, y)
    Xr = np.delete(X, j, axis=1)
    br, er = ols(Xr, y)
    fit = Xr @ br
    w6 = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
    gs = np.unique(cl)
    ts = []
    for _ in range(B):
        wg = dict(zip(gs, rng.choice(w6, len(gs))))
        ystar = fit + er * np.array([wg[g] for g in cl])
        ts.append(tstat(X, ystar))
    ts = np.array(ts)
    return b[j], t0, float((np.abs(ts) >= abs(t0)).mean())


def main() -> None:
    daily = pd.read_parquet(DERIVED / "returns_daily.parquet")
    weekly = pd.read_parquet(DERIVED / "returns_weekly.parquet")
    ex = pd.read_csv(TABLES / "dc_exposure_candidates.csv")
    e23 = ex[ex.vintage == "FY2023"][["ticker", "mentions_per_10k", "dc_mentions"]].copy()
    e23["any_mention"] = (e23.dc_mentions > 0).astype(int)
    e24 = ex[ex.vintage == "FY2024"][["ticker", "mentions_per_10k"]].copy()
    e24["rank_fy2024"] = e24.mentions_per_10k.rank()
    plc = pd.read_csv(TABLES / "dc_exposure_placebo.csv")[["ticker", "mentions_per_10k"]]
    hub = pd.read_csv(TABLES.parent.parent / "data" / "classification" / "hub_flags_nonus.csv")[["ticker", "hub_flag"]]

    u = utility_table(daily)
    u.to_csv(TABLES / "h1_utility_betas.csv", index=False, float_format="%.5f")
    tests = []

    def add(name, r):
        tests.append({"test": name, **r})

    add("main: US d_b_ai on FY2023 mentions per 10k", us_test(u, e23))
    add("US d_partialR2 on FY2023 mentions per 10k", us_test(u, e23, "d_pr2_ai"))
    # pooled placebo
    us = u[u.country == "US"]
    el = us[us.role == "regulated_electric"].merge(e23, on="ticker")[["ticker", "d_b_ai", "mentions_per_10k"]]
    pl = us[us.role.isin(["placebo_water", "placebo_gas"])].merge(plc, on="ticker")[["ticker", "d_b_ai", "mentions_per_10k"]]
    el["placebo"], pl["placebo"] = 0, 1
    pool = pd.concat([el, pl])
    X = np.column_stack([np.ones(len(pool)), pool.mentions_per_10k, pool.placebo])
    b, se = hc1(X, pool.d_b_ai.values)
    add("placebo: indicator in pooled US regression", {"slope": b[2], "se": se[2], "t": b[2] / se[2],
                                                       "intercept": b[0], "n": len(pool)})
    # all-country specification
    el_all = u[u.role == "regulated_electric"].copy()
    el_all = el_all.merge(e23[["ticker", "mentions_per_10k"]], on="ticker", how="left").merge(hub, on="ticker", how="left")
    el_all["expo_raw"] = np.where(el_all.country == "US", el_all.mentions_per_10k, el_all.hub_flag)
    el_all["expo_z"] = el_all.groupby("country").expo_raw.transform(
        lambda s: (s - s.mean()) / s.std() if s.std() > 0 else s * 0)
    D = pd.get_dummies(el_all.country, drop_first=True).astype(float)
    X = np.column_stack([np.ones(len(el_all)), el_all.expo_z, D.values])
    coef, t0, pval = webb_boot(X, el_all.d_b_ai.values, el_all.country.values, 1)
    add("secondary: all countries, within-country z exposure, country FE (wild cluster bootstrap p)",
        {"slope": coef, "se": np.nan, "t": t0, "intercept": np.nan, "n": len(el_all), "p_boot": pval})
    # robustness
    add("rob1: NVDA as AI factor", us_test(utility_table(daily, ai="nvda"), e23))
    add("rob3: excluding EIX and PCG", us_test(u[~u.ticker.isin(["EIX", "PCG"])], e23))
    add("rob4: AI era from 2024-01-01", us_test(utility_table(daily, post=("2024-01-01", POST[1])), e23))
    add("rob5: weekly returns", us_test(utility_table(weekly), e23))
    add("rob6a: FY2024 exposure in ranks", us_test(u, e24, col="rank_fy2024"))
    add("rob6b: FY2023 any-mention indicator", us_test(u, e23, col="any_mention"))
    # placebo breaks for the main test
    rng = np.random.default_rng(SEED)
    lo, hi = pd.Timestamp("2015-01-01"), pd.Timestamp("2021-12-31")
    breaks = lo + pd.to_timedelta(rng.integers(0, (hi - lo).days + 1, NDRAW), unit="D")
    us_el = daily[(daily.country == "US") & (daily.role == "regulated_electric")]
    pb = []
    for B in breaks:
        pre = (max(B - LPRE, DATA_START), B)
        post = (B + pd.Timedelta(days=GAP_DAYS), min(B + pd.Timedelta(days=GAP_DAYS) + LPOST, AI_START))
        ut = utility_table(us_el, pre=(str(pre[0].date()), str(pre[1].date())),
                           post=(str(post[0].date()), str(post[1].date())))
        r = us_test(ut, e23)
        pb.append({"break": B.date(), "slope": r["slope"], "n": r["n"]})
    pb = pd.DataFrame(pb)
    pb.to_csv(TABLES / "h1_placebo_breaks.csv", index=False)
    main_slope = tests[0]["slope"]
    tests[0]["p_placebo_one_sided"] = float((pb.slope >= main_slope).mean())
    tests[0]["p_placebo_two_sided"] = float((pb.slope.abs() >= abs(main_slope)).mean())
    out = pd.DataFrame(tests)
    out.to_csv(TABLES / "h1_tests.csv", index=False, float_format="%.5f")
    pd.set_option("display.width", 220)
    print(out.round(4).to_string(index=False))
    s = u.groupby(["country", "role"])[["b_ai_pre", "b_ai_post", "d_b_ai", "d_pr2_ai"]].mean().round(3)
    print(s.to_string())


if __name__ == "__main__":
    main()
