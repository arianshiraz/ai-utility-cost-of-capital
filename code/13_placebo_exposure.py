"""FY2023 data-centre exposure for the US water and gas placebo utilities (docs/analysis_notes.md, H1).

Same measure and method as code/03_dc_exposure_measures.py: data-centre mentions per 10,000
words of the main FY2023 10-K (filed January to March 2024). The filing is read in memory.
Output: output/tables/dc_exposure_placebo.csv. SEC requires a contact: set SEC_USER_AGENT.
"""
import importlib.util
import json
import re
from pathlib import Path

import pandas as pd

from config import TABLES, UTILITIES

_s = importlib.util.spec_from_file_location("x", Path(__file__).with_name("03_dc_exposure_measures.py"))
x = importlib.util.module_from_spec(_s)
_s.loader.exec_module(x)
collect = x.collect


def main() -> None:
    u = pd.read_csv(UTILITIES)
    tickers = u[(u.country == "US") & u.role.isin(["placebo_water", "placebo_gas"])].ticker.tolist()
    cmap = json.loads(collect.get("https://www.sec.gov/files/company_tickers.json"))
    cik = {v["ticker"]: int(v["cik_str"]) for v in cmap.values() if v["ticker"] in tickers}
    rows = []
    for t in tickers:
        sub = json.loads(collect.get(f"https://data.sec.gov/submissions/CIK{cik[t]:010d}.json"))["filings"]["recent"]
        url = ""
        for i, f in enumerate(sub["form"]):
            # FY2023 10-K: filed January to March 2024, or October 2023 to March 2024 for
            # September fiscal-year filers (Atmos, Spire)
            if f == "10-K" and "2023-10-01" <= sub["filingDate"][i] <= "2024-03-31":
                url = (f"https://www.sec.gov/Archives/edgar/data/{cik[t]}/"
                       f"{sub['accessionNumber'][i].replace('-', '')}/{sub['primaryDocument'][i]}")
                break
        text = x.to_text(collect.get(url)) if url else ""
        m, w = len(x.DC.findall(text)), len(text.split())
        rows.append({"ticker": t, "vintage": "FY2023", "tenk_found": bool(url), "dc_mentions": m,
                     "tenk_words": w, "mentions_per_10k": 1e4 * m / w if w else 0.0, "url": url})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "dc_exposure_placebo.csv", index=False, float_format="%.3f")
    print(out.drop(columns="url").to_string(index=False))


if __name__ == "__main__":
    main()
