"""Daily and weekly returns and factors (docs/prespecification.md section 1; docs/analysis_notes.md).

Output data/derived/returns_daily.parquet and returns_weekly.parquet, long format:
  date, ticker, country, role, r (utility log return), m (local index), smh, nvda (local-currency
  log returns of the AI factors, not yet orthogonalised), dy (change in 10-year yield, pp),
  dy_bund (German yield change, Italy robustness).
Orthogonalisation is done inside each estimation window by the test scripts.
"""
import numpy as np
import pandas as pd

from config import DERIVED, RAW, UTILITIES

INDEX = {"US": "^GSPC", "UK": "^FTAS", "DE": "^GDAXI", "ES": "^IBEX", "IT": "FTSEMIB.MI", "CA": "^GSPTSE"}
FX = {"UK": "GBPUSD=X", "DE": "EURUSD=X", "ES": "EURUSD=X", "IT": "EURUSD=X", "CA": "CADUSD=X"}
YIELD = {"US": "US", "UK": "UK", "DE": "DE", "ES": "ES", "IT": "IT_EA_ALL", "CA": "CA"}


def main() -> None:
    p = pd.read_csv(RAW / "prices_yf.csv", index_col=0, parse_dates=True).sort_index()
    y = pd.read_csv(DERIVED / "yields_daily.csv", parse_dates=["date"]).pivot_table(
        index="date", columns="country", values="yield_pct")
    u = pd.read_csv(UTILITIES)
    u = u[u.country.isin(INDEX)]
    frames = {"daily": [], "weekly": []}
    for c, idx in INDEX.items():
        fx = p[FX[c]] if c in FX else pd.Series(1.0, index=p.index)
        ai = pd.DataFrame({"smh": p["SMH"] / fx, "nvda": p["NVDA"] / fx})
        for freq in ("daily", "weekly"):
            # prices on the local index's trading days; weekly = Friday close
            base = pd.concat({"m": p[idx], "smh": ai.smh, "nvda": ai.nvda, "y": y[YIELD[c]],
                              "y_bund": y["DE"]}, axis=1).reindex(p.index)
            base = base[p[idx].notna().values]
            if freq == "weekly":
                base = base.resample("W-FRI").last()
            fac = pd.DataFrame({"m": np.log(base.m).diff(), "smh": np.log(base.smh).diff(),
                                "nvda": np.log(base.nvda).diff(), "dy": base.y.diff(),
                                "dy_bund": base.y_bund.diff()})
            for _, row in u[u.country == c].iterrows():
                px = p[row.ticker].reindex(base.index) if freq == "daily" else \
                    p[row.ticker][p[idx].notna()].resample("W-FRI").last()
                df = fac.copy()
                df["r"] = np.log(px).diff()
                df["ticker"], df["country"], df["role"] = row.ticker, c, row.role
                frames[freq].append(df.dropna(subset=["r", "m", "smh", "dy"]).reset_index(names="date"))
    for freq, fr in frames.items():
        out = pd.concat(fr, ignore_index=True)
        out.to_parquet(DERIVED / f"returns_{freq}.parquet", index=False)
        print(freq, out.shape, out.date.min().date(), out.date.max().date(), out.ticker.nunique(), "tickers")


if __name__ == "__main__":
    main()
