"""Build candidate data-centre exposure measures from the collected 10-K filings, per vintage.

Measures (both vintages, for comparison before the exposure rule is frozen):
  mentions_per_10k  data-centre mentions per 10,000 words of the 10-K (0 if not mentioned)
  any_mw            1 if any 10-K or 8-K sentence pairs data centres with an MW/GW figure
  share_sentences   10-K sentences pairing data centres with a percentage (for hand-coding
                    a data-centre share of sales where disclosed)
Output: output/tables/dc_exposure_candidates.csv and dc_share_sentences.csv
"""
import html
import importlib.util
import json
import re
from pathlib import Path

import pandas as pd

from config import RAW, TABLES, UTILITIES

_spec = importlib.util.spec_from_file_location(
    "collect", Path(__file__).with_name("02_collect_dc_disclosures.py"))
collect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(collect)
WINDOWS = collect.VINTAGES


def main_10k(cik: int, ticker: str, vint: str) -> Path | None:
    """Download the primary 10-K document filed in the vintage window (not exhibits)."""
    out = RAW / "sec" / vint / ticker / "10k_main.htm"
    if out.exists():
        return out
    sub = json.loads(collect.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    r = sub["filings"]["recent"]
    start, end = WINDOWS[vint]
    for i, form in enumerate(r["form"]):
        if form == "10-K" and start <= r["filingDate"][i] <= end:
            url = (f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                   f"{r['accessionNumber'][i].replace('-', '')}/{r['primaryDocument'][i]}")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(collect.get(url))
            return out
    return None

DC = re.compile(r"data[\s-]?cent(?:er|re)s?", re.I)
PCT = re.compile(r"\d+(?:\.\d+)?\s?%|\d+(?:\.\d+)?\s?percent", re.I)


def to_text(raw: bytes) -> str:
    s = raw.decode("utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s))


def main() -> None:
    utils = pd.read_csv(UTILITIES)
    tickers = utils.loc[(utils["country"] == "US") & (utils["role"] == "regulated_electric"),
                        "ticker"].tolist()
    snips = pd.read_csv(TABLES / "dc_snippets.csv")
    cmap = json.loads(collect.get("https://www.sec.gov/files/company_tickers.json"))
    cik = {v["ticker"]: int(v["cik_str"]) for v in cmap.values() if v["ticker"] in tickers}
    rows, shares = [], []
    for vint in ["FY2023", "FY2024"]:
        for t in tickers:
            f = main_10k(cik[t], t, vint)
            mentions = words = 0
            if f is not None:
                text = to_text(f.read_bytes())
                mentions = len(DC.findall(text))
                words = len(text.split())
                for sent in re.split(r"(?<=[.;])\s+", text):
                    if DC.search(sent) and PCT.search(sent) and len(sent) < 1200:
                        shares.append({"ticker": t, "vintage": vint, "sentence": sent.strip()})
            rows.append({"ticker": t, "vintage": vint, "tenk_found": f is not None,
                         "dc_mentions": mentions, "tenk_words": words,
                         "mentions_per_10k": 1e4 * mentions / words if words else 0.0,
                         "any_mw": int(((snips.ticker == t) & (snips.vintage == vint)).any())})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "dc_exposure_candidates.csv", index=False, float_format="%.3f")
    pd.DataFrame(shares).drop_duplicates().to_csv(TABLES / "dc_share_sentences.csv", index=False)
    wide = out.pivot(index="ticker", columns="vintage", values="mentions_per_10k").reindex(tickers)
    wide["any_mw_FY24"] = out[out.vintage == "FY2024"].set_index("ticker")["any_mw"]
    print(wide.round(2).to_string())
    for v in ["FY2023", "FY2024"]:
        s = out[out.vintage == v]
        print(v, "firms mentioning data centres in 10-K:", int((s.dc_mentions > 0).sum()), "of", len(s))
    print("Spearman rank correlation FY2023 vs FY2024:",
          round(wide["FY2023"].corr(wide["FY2024"], method="spearman"), 2))


if __name__ == "__main__":
    main()
