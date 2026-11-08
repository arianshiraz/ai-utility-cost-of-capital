"""H3 US panel and H4 for US units (docs/prespecification.md section 4; docs/analysis_notes.md).

For each in-panel rate decision: the holding company's Value Line-style beta (5 years of weekly
returns against the S&P 500 ending the Friday before the order month, Blume-adjusted) and its
counterfactual (both counterfactuals); c = adjusted beta minus counterfactual adjusted beta.
Panel: consecutive decisions of the same unit; change in authorised ROE (pp) on change in c,
controlling for changes in the 10-year Treasury yield and the Baa spread (30-day means before the
order month), with and without state fixed effects; standard errors clustered by state, wild
cluster bootstrap. H4: basis points times equity in rate base, per year and per customer.
Outputs in output/tables/: h3_us_decisions.csv, h3_us_panel.csv, h4_us.csv.
"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from config import DERIVED, TABLES

def _load(name, file):
    s = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

h1 = _load("h1", "14_h1_comovement.py")
rep = _load("rep", "17_h3_replicas.py")
CLS = Path(__file__).resolve().parents[1] / "data" / "classification"


def cluster_se(X, y, cl):
    b, e = h1.ols(X, y)
    XtXi = np.linalg.inv(X.T @ X)
    G = len(np.unique(cl))
    meat = sum(np.outer(X[cl == g].T @ e[cl == g], X[cl == g].T @ e[cl == g]) for g in np.unique(cl))
    n, k = X.shape
    V = XtXi @ meat @ XtXi * G / (G - 1) * (n - 1) / (n - k)
    return b, np.sqrt(np.diag(V))


def main(exclude=(), write=True):
    """Panel and H4. exclude: tickers dropped (robustness check 3); write=False returns results only."""
    wk = pd.read_parquet(DERIVED / "returns_weekly.parquet")
    wk = wk[(wk.country == "US") & ~wk.ticker.isin(exclude)]
    y = pd.read_csv(DERIVED / "yields_daily.csv", parse_dates=["date"]).pivot_table(index="date", columns="country", values="yield_pct")
    dec = pd.read_csv(CLS / "ratecase_decisions.csv", dtype=str).fillna("")
    dec = dec[(dec.in_panel == "1") & dec.order_date.str.match(r"^\d{4}-\d{2}$") & (dec.roe_authorised_pct != "")
              & ~dec.ticker.isin(exclude)].copy()
    dec["date"] = pd.to_datetime(dec.order_date + "-01")
    dec["roe"] = dec.roe_authorised_pct.astype(float)
    cache, rows, dropped = {}, [], []
    for _, d in dec.iterrows():
        t = d.ticker
        df = wk[wk.ticker == t].sort_values("date")
        if t not in cache:
            cache[t] = rep.loadings(df)
        L = cache[t]
        end = d.date - pd.Timedelta(days=1)
        start = end - pd.DateOffset(years=5)
        w = df[(df.date > start) & (df.date <= end)]
        if len(w) < 104:
            dropped.append({"ticker": t, "order_date": d.order_date, "weeks": len(w)})
            continue
        be = rep.slope(w.r.values, w.m.values)
        cfb = {}
        for which in ("exposure", "composition", "both"):
            wc = rep.counterfactual(df, L, which)
            wc = wc[(wc.date > start) & (wc.date <= end)]
            cfb[which] = rep.slope(wc.r_cf.values, wc.m_cf.values)
        be_cf = cfb["both"]
        win = (d.date - pd.Timedelta(days=30), d.date - pd.Timedelta(days=1))
        rows.append({"ticker": t, "state": d.state, "order_date": d.order_date, "date": d.date, "roe": d.roe,
                     "beta_raw": be, "beta_adj": 0.67 * be + 0.33, "beta_cf_adj": 0.67 * be_cf + 0.33,
                     "c": 0.67 * (be - be_cf), "c_exposure": 0.67 * (be - cfb["exposure"]),
                     "c_composition": 0.67 * (be - cfb["composition"]),
                     "index_smh_slope_pre": L["pre"]["g"], "index_smh_slope_ai": L["ai"]["g"],
                     "t10": y["US"].loc[win[0]:win[1]].mean(), "baa": y["US_BAA10Y"].loc[win[0]:win[1]].mean(),
                     "weeks": len(w)})
    D = pd.DataFrame(rows).sort_values(["ticker", "date"])
    if write:
        D.to_csv(TABLES / "h3_us_decisions.csv", index=False, float_format="%.5f")
    P = D.copy()
    for col in ("roe", "c", "t10", "baa"):
        P[f"d_{col}"] = P.groupby("ticker")[col].diff()
    P = P.dropna(subset=["d_roe"])
    res = []
    cl = P.state.values
    base = np.column_stack([np.ones(len(P)), P.d_c, P.d_t10, P.d_baa])
    b, se = cluster_se(base, P.d_roe.values, cl)
    _, t0, pb = h1.webb_boot(base, P.d_roe.values, cl, 1)
    res.append({"spec": "no fixed effects", "coef_d_c": b[1], "se": se[1], "t": b[1] / se[1], "p_boot": pb,
                "coef_d_t10": b[2], "coef_d_baa": b[3], "n_pairs": len(P), "n_states": len(np.unique(cl))})
    FE = pd.get_dummies(P.state, drop_first=True).astype(float).values
    Xf = np.column_stack([base, FE])
    b, se = cluster_se(Xf, P.d_roe.values, cl)
    _, t0, pb = h1.webb_boot(Xf, P.d_roe.values, cl, 1)
    res.append({"spec": "state fixed effects (pre-specified)", "coef_d_c": b[1], "se": se[1], "t": b[1] / se[1],
                "p_boot": pb, "coef_d_t10": b[2], "coef_d_baa": b[3], "n_pairs": len(P), "n_states": len(np.unique(cl))})
    R = pd.DataFrame(res)
    if not write:
        return R, D
    R.to_csv(TABLES / "h3_us_panel.csv", index=False, float_format="%.5f")

    # H4: latest AI-era decision per unit
    rb = pd.read_csv(TABLES / "ratecase_rate_base_proxy.csv")
    st = pd.read_csv(CLS / "ratecase_rate_base_stated.csv")
    eq = pd.read_csv(CLS / "ratecase_decisions.csv", dtype=str)
    coef = R.loc[R.spec.str.startswith("state"), "coef_d_c"].iloc[0]
    h4 = []
    last = D[D.date >= pd.Timestamp("2023-01-01")].sort_values("date").groupby("ticker").tail(1)
    for _, r in last.iterrows():
        yr = min(r.date.year, 2025)
        prox = rb[(rb.ticker == r.ticker) & (rb.year == yr)].rate_base_proxy
        stated = st[st.ticker == r.ticker].rate_base_stated
        rbase = float(stated.iloc[0]) if len(stated) else (float(prox.iloc[0]) if len(prox) else np.nan)
        e = eq[(eq.ticker == r.ticker) & (eq.order_date == r.order_date)].equity_ratio_pct
        eshare = float(e.iloc[0]) / 100 if len(e) and e.iloc[0] not in ("", "nan") else 0.50
        cust = rb[rb.ticker == r.ticker].customers_2023.iloc[0]
        for label, bps in (("observed pass-through", coef * r.c * 100), ("upper bound, 6% premium, full CAPM weight", r.c * 0.06 * 1e4)):
            usd = bps / 1e4 * eshare * rbase
            h4.append({"ticker": r.ticker, "order_date": r.order_date, "c": r.c, "basis": label, "bps": bps,
                       "rate_base": rbase, "rate_base_source": "stated" if len(stated) else "FERC proxy (upper bound)",
                       "equity_share": eshare, "usd_per_year": usd, "usd_per_customer_year": usd / cust})
    H = pd.DataFrame(h4)
    H.to_csv(TABLES / "h4_us.csv", index=False, float_format="%.5f")
    pd.set_option("display.width", 220)
    print("dropped (short windows):", dropped)
    print(D[D.date >= "2023-01-01"][["c", "c_exposure", "c_composition"]].describe().round(4).to_string())
    print(R.round(4).to_string(index=False))
    print(H.groupby("basis")[["bps", "usd_per_year", "usd_per_customer_year"]].agg(["median", "max"]).round(2).to_string())
    return R, D


if __name__ == "__main__":
    main()
