"""Collect data-centre disclosures from SEC filings for the exposure measure (decision D4).

For each US utility and each vintage window, find 10-K and 8-K documents mentioning data
centres (EDGAR full-text search), download them, and keep every sentence that mentions data
centres, large loads or hyperscalers together with a megawatt or gigawatt figure. The
sentences are the evidence base for hand-coding signed, advanced and early-stage MW
(docs/exposure_rule.md).

SEC requires a contact in the User-Agent: set the environment variable SEC_USER_AGENT
(for example "Your Name your@email"). It is read at run time and never stored in the repo.

Outputs: data/raw/sec/<vintage>/<ticker>/<file> (raw documents, not committed) and
output/tables/dc_snippets.csv (ticker, vintage, form, filing date, url, sentence).
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import pandas as pd

from config import RAW, TABLES, UTILITIES

VINTAGES = {"FY2023": ("2024-01-01", "2024-03-31"), "FY2024": ("2025-01-01", "2025-03-31")}
FORMS = {"10-K", "8-K"}
TOPIC = re.compile(r"data.?cent|large.?load|hyperscal", re.I)
SIZE = re.compile(r"\b\d[\d,.]*\s*(MW|GW|megawatt|gigawatt)", re.I)


def ua() -> str:
    agent = os.environ.get("SEC_USER_AGENT")
    if not agent:
        sys.exit("Set SEC_USER_AGENT (for example 'Your Name your@email') before running.")
    return agent


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": ua(), "Accept-Encoding": "identity"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                time.sleep(0.15)  # stay well under SEC's 10 requests per second
                return r.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


def to_text(raw: bytes) -> str:
    s = raw.decode("utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s))


def main() -> None:
    utils = pd.read_csv(UTILITIES)
    tickers = utils.loc[(utils["country"] == "US") & (utils["role"] == "regulated_electric"),
                        "ticker"].tolist()
    cmap = json.loads(get("https://www.sec.gov/files/company_tickers.json"))
    cik = {v["ticker"]: int(v["cik_str"]) for v in cmap.values() if v["ticker"] in tickers}

    rows, docs_log = [], []
    for vint, (start, end) in VINTAGES.items():
        for t in tickers:
            params = urllib.parse.urlencode({"q": '"data center" OR "data centers"',
                                             "dateRange": "custom", "startdt": start,
                                             "enddt": end, "ciks": f"{cik[t]:010d}"})
            hits = json.loads(get("https://efts.sec.gov/LATEST/search-index?" + params))["hits"]["hits"]
            seen = set()
            for h in hits:
                src = h["_source"]
                form = src.get("form", "")
                if form not in FORMS:
                    continue
                adsh, fname = h["_id"].split(":")
                if (adsh, fname) in seen:
                    continue
                seen.add((adsh, fname))
                url = f"https://www.sec.gov/Archives/edgar/data/{cik[t]}/{adsh.replace('-', '')}/{fname}"
                out = RAW / "sec" / vint / t / fname
                out.parent.mkdir(parents=True, exist_ok=True)
                if not out.exists():
                    out.write_bytes(get(url))
                text = to_text(out.read_bytes())
                n = 0
                for sent in re.split(r"(?<=[.;])\s+", text):
                    if TOPIC.search(sent) and SIZE.search(sent) and len(sent) < 1500:
                        rows.append({"ticker": t, "vintage": vint, "form": form,
                                     "filing_date": src.get("file_date"), "url": url,
                                     "sentence": sent.strip()})
                        n += 1
                docs_log.append({"ticker": t, "vintage": vint, "form": form,
                                 "filing_date": src.get("file_date"), "url": url,
                                 "n_sentences": n})
            print(f"{vint} {t}: {len(seen)} docs")

    TABLES.mkdir(parents=True, exist_ok=True)
    snip = pd.DataFrame(rows).drop_duplicates(["ticker", "vintage", "sentence"])
    snip.to_csv(TABLES / "dc_snippets.csv", index=False)
    pd.DataFrame(docs_log).to_csv(TABLES / "dc_documents.csv", index=False)
    summary = snip.groupby(["ticker", "vintage"]).size().unstack(fill_value=0)
    print(summary.reindex(tickers, fill_value=0).to_string())


if __name__ == "__main__":
    main()
