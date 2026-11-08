"""H3 and H4: counterfactual replicas of regulators' betas (docs/prespecification.md section 4;
docs/analysis_notes.md, "H3 and H4").

Counterfactual returns on AI-era dates (from 30 November 2022):
  exposure:    r_cf = r - (b_ai,AI - b_ai,pre) * ai_perp
  composition: m_cf = m - (g_AI - g_pre) * smh
The loadings come from the H1 windows. The replica beta is the OLS slope of r on m in the
regulator's window; the counterfactual beta uses the counterfactual series.
UK (RIIO-3): output/tables/h3_uk_replica.csv, h3_uk_summary.csv.
Germany (prospective): output/tables/h3_de_replica.csv, h3_de_summary.csv.
Spain (2026-2031 rate): output/tables/h3_es_replica.csv, h3_es_summary.csv.
"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from config import DERIVED, TABLES

_s = importlib.util.spec_from_file_location("h1", Path(__file__).with_name("14_h1_comovement.py"))
h1 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(h1)

AI_DATE = pd.Timestamp("2022-11-30")
CLS = Path(__file__).resolve().parents[1] / "data" / "classification"


def in_window(df, start, end, covid=True):
    w = df[(df.date >= start) & (df.date <= end)]
    if covid:
        w = w[~((w.date >= h1.COVID[0]) & (w.date <= h1.COVID[1]))]
    return w


def loadings(df):
    """AI loading of the firm (three-factor, ai orthogonalised) and of the index on raw smh, per H1 window,
    plus the AI-era orthogonalisation used to build ai_perp on AI-era dates."""
    out = {}
    for tag, (a, b) in (("pre", h1.PRE), ("ai", h1.POST)):
        w = in_window(df, pd.Timestamp(a), pd.Timestamp(b))
        one = np.ones(len(w))
        k, ai_perp = h1.ols(np.column_stack([one, w.m.values]), w.smh.values)
        bb, _ = h1.ols(np.column_stack([one, w.m.values, ai_perp, w.dy.values]), w.r.values)
        g, _ = h1.ols(np.column_stack([one, w.smh.values]), w.m.values)
        out[tag] = {"b_ai": bb[2], "g": g[1], "orth": k}
    return out


def counterfactual(df, L, which):
    d = df.copy()
    ai = d.date >= AI_DATE
    k = L["ai"]["orth"]
    ai_perp = d.smh - (k[0] + k[1] * d.m)
    d["r_cf"], d["m_cf"] = d.r, d.m
    if which in ("exposure", "both"):
        d.loc[ai, "r_cf"] = d.r[ai] - (L["ai"]["b_ai"] - L["pre"]["b_ai"]) * ai_perp[ai]
    if which in ("composition", "both"):
        d.loc[ai, "m_cf"] = d.m[ai] - (L["ai"]["g"] - L["pre"]["g"]) * d.smh[ai]
    return d


def slope(y, x):
    x = x - x.mean()
    return float((x * (y - y.mean())).sum() / (x ** 2).sum())


def uk() -> None:
    daily = pd.read_parquet(DERIVED / "returns_daily.parquet")
    of = pd.read_csv(CLS / "ofgem_dd_comparator_betas.csv")
    of = of[of.asset_beta_10y.notna()]
    end = pd.Timestamp("2025-03-31")
    start = end - pd.DateOffset(years=10)
    debt_beta, gearing_notional, mrp = 0.075, 0.55, 0.069 - 0.023
    rows = []
    for _, c in of.iterrows():
        df = daily[daily.ticker == c.ticker].sort_values("date")
        L = loadings(df)
        w = in_window(df, start, end, covid=False)  # regulators keep all days
        be = slope(w.r.values, w.m.values)
        g = (be - c.asset_beta_10y) / (be - debt_beta)
        row = {"company": c.company, "ticker": c.ticker, "country": c.country, "ofgem_asset_beta_10y": c.asset_beta_10y,
               "replica_equity_beta": be, "implied_gearing": g, "gearing_plausible": bool(0.2 <= g <= 0.75),
               "b_ai_pre": L["pre"]["b_ai"], "b_ai_ai": L["ai"]["b_ai"], "g_pre": L["pre"]["g"], "g_ai": L["ai"]["g"],
               "n_days": len(w)}
        for which in ("exposure", "composition", "both"):
            wc = in_window(counterfactual(df, L, which), start, end, covid=False)
            be_cf = slope(wc.r_cf.values, wc.m_cf.values)
            row[f"equity_beta_cf_{which}"] = be_cf
            row[f"d_asset_beta_{which}"] = (1 - g) * (be - be_cf)  # actual minus counterfactual
        rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(TABLES / "h3_uk_replica.csv", index=False, float_format="%.5f")
    summ = []
    for which in ("exposure", "composition", "both"):
        d_all = t[f"d_asset_beta_{which}"].mean()
        dom = t.loc[t.country == "UK", f"d_asset_beta_{which}"].sum() / len(t)
        d_eq = d_all / (1 - gearing_notional)
        summ.append({"counterfactual": which, "replica_asset_beta": t.ofgem_asset_beta_10y.mean(),
                     "published_asset_beta": 0.375, "d_asset_beta": d_all, "of_which_domestic": dom,
                     "of_which_foreign": d_all - dom, "d_equity_beta_notional": d_eq, "bps": d_eq * mrp * 1e4,
                     "gbp_per_bn_rav_per_year": d_eq * mrp * (1 - gearing_notional) * 1e9})
    s = pd.DataFrame(summ)
    s.to_csv(TABLES / "h3_uk_summary.csv", index=False, float_format="%.5f")
    pd.set_option("display.width", 220)
    print(t[["ticker", "ofgem_asset_beta_10y", "replica_equity_beta", "implied_gearing", "gearing_plausible",
             "b_ai_pre", "b_ai_ai", "d_asset_beta_exposure", "d_asset_beta_composition", "d_asset_beta_both"]].round(4).to_string(index=False))
    print(s.round(5).to_string(index=False))


DE_MAP = {"NATIONAL GRID PLC": ("NG.L", "^STOXX", "EURUSD=X", "DE"), "REDEIA CORP SA": ("RED.MC", "^STOXX", "EURUSD=X", "DE"),
          "REDES ENERGETICAS NACIONAIS": ("RENE.LS", "^STOXX", "EURUSD=X", "DE"),
          "TERNA-RETE ELETTRICA NAZIONALE": ("TRN.MI", "^STOXX", "EURUSD=X", "DE"), "ELIA GROUP SA/NV": ("ELI.BR", "^STOXX", "EURUSD=X", "DE"),
          "SNAM SPA": ("SRG.MI", "^STOXX", "EURUSD=X", "DE"), "ENAGAS SA": ("ENG.MC", "^STOXX", "EURUSD=X", "DE"),
          "TC ENERGY CORP": ("TRP.TO", "^GSPTSE", "CADUSD=X", "CA"), "APA GROUP": ("APA.AX", "^AXJO", "AUDUSD=X", "US"),
          "VECTOR LTD": ("VCT.NZ", "^NZ50", "NZDUSD=X", "US"), "ITALGAS SPA": ("IG.MI", "^STOXX", "EURUSD=X", "DE"),
          "ASCOPIAVE SPA": ("ASC.MI", "^STOXX", "EURUSD=X", "DE")}


def de() -> None:
    """Prospective German calculation on the 2026 expert report's comparators (analysis notes)."""
    from config import RAW
    px = pd.read_csv(RAW / "prices_de_comparators.csv", index_col=0, parse_dates=True).sort_index()
    y = pd.read_csv(DERIVED / "yields_daily.csv", parse_dates=["date"]).pivot_table(index="date", columns="country", values="yield_pct")
    fr = pd.read_csv(CLS / "bnetza_frontier_2026_comparator_betas.csv")
    end = pd.Timestamp("2026-10-31")
    debt_beta, equity_share, mrp = 0.075, 0.40, 0.037
    rows = []
    for _, c in fr.iterrows():
        tic, idx, fx, yc = DE_MAP[c.company]
        b = pd.DataFrame({"p": px[tic], "m": px[idx], "smh": px["SMH"] / px[fx]}).dropna()
        d = pd.DataFrame({"date": b.index, "r": np.log(b.p).diff().values, "m": np.log(b.m).diff().values,
                          "smh": np.log(b.smh).diff().values})
        d["dy"] = y[yc].reindex(b.index).diff().values
        d = d.dropna()
        L = loadings(d)
        row = {"company": c.company, "ticker": tic, "index": idx,
               "frontier_asset_beta_3y": c.asset_beta_stoxx600_or_national_3y,
               "frontier_asset_beta_5y": c.asset_beta_stoxx600_or_national_5y,
               "b_ai_pre": L["pre"]["b_ai"], "b_ai_ai": L["ai"]["b_ai"]}
        for yrs in (1, 3, 5):
            w = in_window(d, end - pd.DateOffset(years=yrs), end, covid=False)
            be = slope(w.r.values, w.m.values)
            ref = c.asset_beta_stoxx600_or_national_3y if yrs != 5 else c.asset_beta_stoxx600_or_national_5y
            g = (be - ref) / (be - debt_beta)
            row[f"equity_beta_{yrs}y"], row[f"implied_gearing_{yrs}y"] = be, g
            for which in ("exposure", "composition", "both"):
                wc = in_window(counterfactual(d, L, which), end - pd.DateOffset(years=yrs), end, covid=False)
                row[f"d_asset_beta_{which}_{yrs}y"] = (1 - g) * (be - slope(wc.r_cf.values, wc.m_cf.values))
        rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(TABLES / "h3_de_replica.csv", index=False, float_format="%.5f")
    summ = []
    for yrs in (1, 3, 5):
        ok = t[(t[f"implied_gearing_{yrs}y"] >= 0.2) & (t[f"implied_gearing_{yrs}y"] <= 0.75)]  # plausibility rule, analysis notes
        for which in ("exposure", "composition", "both"):
            da = ok[f"d_asset_beta_{which}_{yrs}y"].mean()
            summ.append({"window_years": yrs, "counterfactual": which, "n_comparators_used": len(ok),
                         "d_asset_beta": da, "d_equity_beta_notional": da / equity_share,
                         "bps": da / equity_share * mrp * 1e4})
    s = pd.DataFrame(summ)
    s.to_csv(TABLES / "h3_de_summary.csv", index=False, float_format="%.5f")
    pd.set_option("display.width", 240)
    print(t[["ticker", "frontier_asset_beta_3y", "equity_beta_3y", "implied_gearing_3y", "implied_gearing_5y",
             "d_asset_beta_both_1y", "d_asset_beta_both_3y", "d_asset_beta_both_5y"]].round(3).to_string(index=False))
    print(s.round(4).to_string(index=False))


# CNMC memo, Cuadro 26 (p115): levered beta, D/E, statutory tax, unlevered beta; liquid comparators only
# (bid-ask spread at most 1%); EDF has no price history after its 2023 delisting.
ES_COMP = [("E.ON", "EOAN.DE", "^GDAXI", 0.71, 0.98, 0.2995, 0.42), ("EVN", "EVN.VI", "^ATX", 0.68, 0.35, 0.24, 0.53),
           ("Verbund", "VER.VI", "^ATX", 0.66, 0.11, 0.24, 0.61), ("Elia Group", "ELI.BR", "^BFX", 0.52, 0.80, 0.25, 0.33),
           ("Enagas", "ENG.MC", "^IBEX", 0.58, 0.80, 0.25, 0.36), ("Endesa", "ELE.MC", "^IBEX", 0.69, 0.45, 0.25, 0.51),
           ("Iberdrola", "IBE.MC", "^IBEX", 0.66, 0.76, 0.25, 0.42), ("Naturgy", "NTGY.MC", "^IBEX", 0.68, 0.60, 0.25, 0.47),
           ("Redeia", "RED.MC", "^IBEX", 0.47, 0.67, 0.25, 0.31), ("Engie", "ENGI.PA", "^FCHI", 1.02, 0.82, 0.2583, 0.63),
           ("PPC", "PPC.AT", "GD.AT", 1.34, 1.94, 0.22, 0.53), ("ADMIE", "ADMIE.AT", "GD.AT", 0.75, -0.02, 0.22, 0.77),
           ("A2A", "A2A.MI", "FTSEMIB.MI", 0.82, 0.80, 0.2781, 0.52), ("Acea", "ACE.MI", "FTSEMIB.MI", 0.67, 1.19, 0.2781, 0.36),
           ("Ascopiave", "ASC.MI", "FTSEMIB.MI", 0.71, 0.41, 0.2781, 0.55), ("Enel", "ENEL.MI", "FTSEMIB.MI", 0.89, 0.99, 0.2781, 0.52),
           ("Hera", "HER.MI", "FTSEMIB.MI", 0.67, 0.75, 0.2781, 0.43), ("Iren", "IRE.MI", "FTSEMIB.MI", 0.81, 1.19, 0.2781, 0.44),
           ("Italgas", "IG.MI", "FTSEMIB.MI", 0.58, 1.14, 0.2781, 0.32), ("SNAM", "SRG.MI", "FTSEMIB.MI", 0.63, 0.84, 0.2781, 0.39),
           ("Terna", "TRN.MI", "FTSEMIB.MI", 0.54, 0.72, 0.2781, 0.36), ("EDP", "EDP.LS", "PSI20.LS", 0.90, 1.02, 0.315, 0.53),
           ("REN", "RENE.LS", "PSI20.LS", 0.58, 1.49, 0.315, 0.29), ("National Grid", "NG.L", "^FTSE", 0.61, 1.04, 0.25, 0.34),
           ("SSE", "SSE.L", "^FTSE", 0.89, 0.59, 0.25, 0.62)]


def es() -> None:
    from config import RAW
    px = pd.read_csv(RAW / "prices_es_comparators.csv", index_col=0, parse_dates=True).sort_index()
    y = pd.read_csv(DERIVED / "yields_daily.csv", parse_dates=["date"]).pivot_table(index="date", columns="country", values="yield_pct")
    start, end = pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")
    de_reg, tax_es, prm = 0.85, 0.25, 0.0498
    rows = []
    for name, tic, idx, bl, de_r, tax, bu in ES_COMP:
        uk = tic.endswith(".L")
        fx = px["GBPUSD=X"] if uk else px["EURUSD=X"]
        b = pd.DataFrame({"p": px[tic], "m": px[idx], "smh": px["SMH"] / fx,
                          "y": y["UK" if uk else "DE"].reindex(px.index)})
        b = b[b.p.notna() & b.m.notna()].resample("W-FRI").last()
        d = pd.DataFrame({"date": b.index, "r": np.log(b.p).diff().values, "m": np.log(b.m).diff().values,
                          "smh": np.log(b.smh).diff().values, "dy": b.y.diff().values}).dropna()
        L = loadings(d)
        w = in_window(d, start, end, covid=False)
        be = slope(w.r.values, w.m.values)
        row = {"company": name, "ticker": tic, "index": idx, "cnmc_levered_beta": bl, "replica_levered_beta": be,
               "gap_levered": be - bl, "cnmc_de": de_r, "tax": tax, "cnmc_unlevered_beta": bu,
               "replica_unlevered_beta": be / (1 + (1 - tax) * de_r), "n_weeks": len(w)}
        for which in ("exposure", "composition", "both"):
            wc = in_window(counterfactual(d, L, which), start, end, covid=False)
            row[f"d_unlevered_{which}"] = (be - slope(wc.r_cf.values, wc.m_cf.values)) / (1 + (1 - tax) * de_r)
        rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(TABLES / "h3_es_replica.csv", index=False, float_format="%.5f")
    relever = 1 + (1 - tax_es) * de_reg
    summ = [{"counterfactual": "replica", "unlevered_beta": t.replica_unlevered_beta.mean(),
             "relevered_beta": t.replica_unlevered_beta.mean() * relever, "published_relevered_beta": 0.75,
             "cnmc_mean_unlevered_same_firms": t.cnmc_unlevered_beta.mean()}]
    for which in ("exposure", "composition", "both"):
        du = t[f"d_unlevered_{which}"].mean()
        summ.append({"counterfactual": which, "d_unlevered_beta": du, "d_relevered_beta": du * relever,
                     "bps": du * relever * prm * 1e4})
    s = pd.DataFrame(summ)
    s.to_csv(TABLES / "h3_es_summary.csv", index=False, float_format="%.5f")
    pd.set_option("display.width", 240)
    print(t[["ticker", "cnmc_levered_beta", "replica_levered_beta", "gap_levered", "d_unlevered_both"]].round(3).to_string(index=False))
    print("mean abs gap levered", round(t.gap_levered.abs().mean(), 3), "| corr", round(np.corrcoef(t.cnmc_levered_beta, t.replica_levered_beta)[0, 1], 2))
    print(s.round(4).to_string(index=False))


if __name__ == "__main__":
    uk()
    de()
    es()
