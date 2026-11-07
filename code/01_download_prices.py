"""Download daily adjusted prices for utilities, market indices, AI factors and FX rates.

Writes data/raw/prices_yf.csv (wide, adjusted close) and data/raw/download_meta.json, and
output/tables/data_coverage.csv (first and last date and observation count per series).
Yahoo data can be revised, so the raw file is kept as downloaded and never edited.
"""
import json
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

from config import AI_FACTORS, END, EXTRA_SERIES, FX, MARKET_INDEX, RAW, START, TABLES, UTILITIES


def main() -> None:
    utils = pd.read_csv(UTILITIES)
    tickers = sorted(set(utils["ticker"]) | set(MARKET_INDEX.values()) | set(AI_FACTORS)
                     | set(FX.values()) | set(EXTRA_SERIES))
    data = yf.download(tickers, start=START, end=END, auto_adjust=True, progress=False,
                       threads=True)
    prices = data["Close"].sort_index()
    RAW.mkdir(parents=True, exist_ok=True)
    prices.to_csv(RAW / "prices_yf.csv")

    cov = []
    for t in tickers:
        s = prices[t].dropna() if t in prices else pd.Series(dtype=float)
        cov.append({"ticker": t, "first": s.index.min().date() if len(s) else None,
                    "last": s.index.max().date() if len(s) else None, "n_obs": len(s)})
    cov = pd.DataFrame(cov).merge(utils[["ticker", "country", "role"]], on="ticker", how="left")
    TABLES.mkdir(parents=True, exist_ok=True)
    cov.to_csv(TABLES / "data_coverage.csv", index=False)

    meta = {"source": "Yahoo Finance via yfinance", "yfinance_version": yf.__version__,
            "downloaded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "start": START, "end": END, "adjusted": True, "n_tickers": len(tickers),
            "missing": cov.loc[cov["n_obs"] == 0, "ticker"].tolist()}
    (RAW / "download_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"saved {prices.shape[1]} series x {prices.shape[0]} days")
    print(cov.sort_values(["country", "first"]).to_string(index=False))


if __name__ == "__main__":
    main()
