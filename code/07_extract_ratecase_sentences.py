"""Extract return-on-equity sentences from SEC filings for the US rate-case panel.

docs/ratecase_rule.md. For each of the 33 US holding companies, every 10-K filed from
1 January 2015 to the sample end and every 10-Q filed in 2026 is read from EDGAR in memory (no
filing is stored). Every sentence that mentions a return on equity (or ROE) with a percentage is
kept, with the sentence before it as context, and tagged with whether it names the holding
company's rate unit or its state commission. Exhibit 21 of the FY2023 10-K is read to check
that each operating utility in data/classification/us_operating_utilities.csv is a subsidiary.

Outputs (reading aids for hand-coding data/classification/ratecase_decisions.csv):
  output/tables/ratecase_filings.csv          every filing read, with its EDGAR URL
  output/tables/roe_sentences.csv             the sentences
  output/tables/ratecase_subsidiary_check.csv operating utilities found in Exhibit 21
Per-company results are cached in data/derived/roe_parts/ so an interrupted run resumes.
SEC requires a contact: set SEC_USER_AGENT.
"""
import html
import importlib.util
import json
import re
from pathlib import Path

import pandas as pd

from config import DERIVED, END, TABLES

_spec = importlib.util.spec_from_file_location(
    "collect", Path(__file__).with_name("02_collect_dc_disclosures.py"))
collect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(collect)

CLS = Path(__file__).resolve().parents[1] / "data" / "classification"
PARTS = DERIVED / "roe_parts"
TENK_FROM, TENQ_FROM = "2015-01-01", "2026-01-01"
EX21_WINDOW = ("2024-01-01", "2024-03-31")
# Earlier filers whose 10-Ks cover the rate unit before the current holding company existed:
# Westar Energy (now Evergy Kansas Central) before Evergy's first 10-K in 2019, and NorthWestern
# Corp before NorthWestern Energy Group's first 10-K in 2024.
PREDECESSORS = {"EVRG": [(54507, "2015-01-01", "2018-12-31")],
                "NWE": [(73088, "2015-01-01", "2023-12-31")]}

UNIT_KEYWORDS = {
    "AEE": r"Ameren Illinois|\bICC\b|Illinois Commerce Commission",
    "AEP": r"Ohio Power|AEP Ohio|\bOPCo\b|\bPUCO\b",
    "AVA": r"Washington|\bWUTC\b|\bUTC\b",
    "BKH": r"Cheyenne Light|Wyoming|\bWPSC\b",
    "CMS": r"Consumers|\bMPSC\b|Michigan",
    "CNP": r"Houston Electric|\bPUCT\b|Texas",
    "D": r"Virginia Power|Dominion Energy Virginia|Virginia Commission|\bSCC\b",
    "DTE": r"DTE Electric|\bMPSC\b|Michigan",
    "DUK": r"Duke Energy Carolinas|\bNCUC\b|North Carolina",
    "ED": r"\bCECONY\b|\bNYSPSC\b|\bNYPSC\b|New York",
    "EIX": r"\bSCE\b|\bCPUC\b|cost of capital",
    "ES": r"NSTAR Electric|\bDPU\b|Massachusetts",
    "ETR": r"Entergy Louisiana|\bLPSC\b|Louisiana",
    "EVRG": r"Evergy Kansas Central|Westar|\bKCC\b|Kansas",
    "EXC": r"\bComEd\b|\bICC\b|Illinois",
    "FE": r"Ohio Companies|\bPUCO\b|Ohio",
    "IDA": r"Idaho Power|\bIPUC\b|Idaho",
    "LNT": r"\bIPL\b|\bIUB\b|Iowa",
    "MGEE": r"\bMGE\b|\bPSCW\b|Wisconsin",
    "NEE": r"\bFPL\b|\bFPSC\b|Florida",
    "NI": r"\bNIPSCO\b|\bIURC\b|Indiana",
    "NWE": r"Montana|\bMPSC\b",
    "OGE": r"\bOG&E\b|\bOCC\b|Oklahoma",
    "OTTR": r"Minnesota|\bMPUC\b",
    "PCG": r"\bCPUC\b|cost of capital",
    "PNW": r"\bAPS\b|\bACC\b|Arizona Corporation",
    "POR": r"\bOPUC\b|Oregon",
    "PPL": r"PPL Electric|\bPUC\b|Pennsylvania",
    "SO": r"Georgia Power|Georgia PSC",
    "SRE": r"\bSDG&E\b|\bCPUC\b|cost of capital",
    "TXNM": r"\bTNMP\b|\bPUCT\b|Texas",
    "WEC": r"Wisconsin Electric|We Energies|\bPSCW\b",
    "XEL": r"NSP-Minnesota|\bMPUC\b|Minnesota",
}
ROE = re.compile(r"return on (?:common )?equity|\bROEs?\b", re.I)
PCT = re.compile(r"\d{1,2}\.\d{1,3}\s?%|\d{1,2}\.\d{1,3}\s?percent|\b\d{1,2}\s?%", re.I)


def to_text(raw: bytes) -> str:
    s = raw.decode("utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?i)<(br|/p|/div|/tr|/li)[^>]*>", ". ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s))


def sentences(text: str, ticker: str) -> list[dict]:
    sents = re.split(r"(?<=[.;])\s+(?=[A-Z(])", text)
    unit = re.compile(UNIT_KEYWORDS[ticker], re.I)
    out = []
    for i, s in enumerate(sents):
        if len(s) > 1500 or not ROE.search(s) or not PCT.search(s):
            continue
        prev = sents[i - 1] if i else ""
        out.append({"position": round(i / max(len(sents), 1), 3),
                    "names_unit": int(bool(unit.search(s) or unit.search(prev))),
                    "context": prev[-400:], "sentence": s})
    return out


def filings(cik: int) -> pd.DataFrame:
    sub = json.loads(collect.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    frames = [pd.DataFrame(sub["filings"]["recent"])]
    for f in sub["filings"].get("files", []):
        frames.append(pd.DataFrame(json.loads(collect.get(f"https://data.sec.gov/submissions/{f['name']}"))))
    d = pd.concat([f for f in frames if len(f)], ignore_index=True)
    return d[["accessionNumber", "filingDate", "form", "primaryDocument", "reportDate"]]


def ex21_names(cik: int, accession: str) -> list[str]:
    """Documents declared as type EX-21 in the filing index."""
    page = collect.get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/"
                       f"{accession}-index.htm").decode("utf-8", errors="replace")
    names = []
    for row in re.findall(r"(?is)<tr.*?</tr>", page):
        if re.search(r">\s*EX-21[.\d]*\s*<", row):
            m = re.search(r'href="[^"]*/([^"/]+)"', row)
            if m:
                names.append(m.group(1))
    return names


def subsidiary_check(t: str, cik: int, subs: pd.DataFrame, filings_t: pd.DataFrame) -> list[dict]:
    k = filings_t[(filings_t.form == "10-K") & (filings_t.filing_date >= EX21_WINDOW[0])
                  & (filings_t.filing_date <= EX21_WINDOW[1])]
    if k.empty:
        return []
    acc_path = k.url.iloc[0].rsplit("/", 2)[1]
    accession = f"{acc_path[:10]}-{acc_path[10:12]}-{acc_path[12:]}"
    cik_f = int(k.url.iloc[0].split("/data/")[1].split("/")[0])
    ex = ex21_names(cik_f, accession)
    text = " ".join(to_text(collect.get(f"https://www.sec.gov/Archives/edgar/data/{cik_f}/{acc_path}/{n}")) for n in ex)
    out = []
    for _, u in subs[subs.ticker == t].iterrows():
        key = re.sub(r"\s*\(.*\)", "", u.operating_utility)
        words = [w for w in re.split(r"\W+", key) if len(w) > 2][:2]
        found = all(re.search(re.escape(w), text, re.I) for w in words) if words else False
        out.append({"ticker": t, "operating_utility": u.operating_utility, "search_words": " ".join(words),
                    "found_in_ex21": int(found),
                    "ex21_url": f"https://www.sec.gov/Archives/edgar/data/{cik_f}/{acc_path}/{ex[0]}" if ex else ""})
    return out


def one_company(t: str, cik: int, subs: pd.DataFrame) -> None:
    d = filings(cik)
    d["cik"] = cik
    keep = d[((d.form == "10-K") & (d.filingDate >= TENK_FROM) & (d.filingDate <= END))
             | ((d.form == "10-Q") & (d.filingDate >= TENQ_FROM) & (d.filingDate <= END))]
    for pc, start, end in PREDECESSORS.get(t, []):
        p = filings(pc)
        p["cik"] = pc
        keep = pd.concat([keep, p[(p.form == "10-K") & (p.filingDate >= start) & (p.filingDate <= end)]])
    fl, rows, check = [], [], []
    for _, r in keep.iterrows():
        acc = r.accessionNumber.replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{r.cik}/{acc}/{r.primaryDocument}"
        fl.append({"ticker": t, "form": r.form, "filing_date": r.filingDate,
                   "report_date": r.reportDate, "url": url})
        for s in sentences(to_text(collect.get(url)), t):
            rows.append({"ticker": t, "form": r.form, "filing_date": r.filingDate, "url": url, **s})
        if r.form == "10-K" and r.cik == cik and EX21_WINDOW[0] <= r.filingDate <= EX21_WINDOW[1]:
            ex = ex21_names(cik, r.accessionNumber)
            text = " ".join(to_text(collect.get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{n}"))
                            for n in ex)
            for _, u in subs[subs.ticker == t].iterrows():
                key = re.sub(r"\s*\(.*\)", "", u.operating_utility)
                words = [w for w in re.split(r"\W+", key) if len(w) > 2][:2]
                found = all(re.search(re.escape(w), text, re.I) for w in words) if words else False
                check.append({"ticker": t, "operating_utility": u.operating_utility,
                              "search_words": " ".join(words), "found_in_ex21": int(found),
                              "ex21_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{ex[0]}" if ex else ""})
    PARTS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(fl).to_csv(PARTS / f"{t}_filings.csv", index=False)
    pd.DataFrame(rows).to_csv(PARTS / f"{t}_sentences.csv", index=False)
    pd.DataFrame(check).to_csv(PARTS / f"{t}_ex21.csv", index=False)
    print(t, len(fl), "filings,", len(rows), "sentences", flush=True)


def main() -> None:
    tickers = pd.read_csv(TABLES / "ratecase_units.csv")["ticker"].tolist()
    subs = pd.read_csv(CLS / "us_operating_utilities.csv")
    cmap = json.loads(collect.get("https://www.sec.gov/files/company_tickers.json"))
    cik = {v["ticker"]: int(v["cik_str"]) for v in cmap.values() if v["ticker"] in tickers}
    for t in tickers:
        if not (PARTS / f"{t}_sentences.csv").exists():
            one_company(t, cik[t], subs)

    def cat(kind: str) -> pd.DataFrame:
        frames = []
        for t in tickers:
            p = PARTS / f"{t}_{kind}.csv"
            if p.exists() and p.stat().st_size > 2:
                frames.append(pd.read_csv(p))
        return pd.concat(frames, ignore_index=True)
    cat("filings").to_csv(TABLES / "ratecase_filings.csv", index=False)
    s = cat("sentences").drop_duplicates(subset=["ticker", "filing_date", "sentence"])
    s.to_csv(TABLES / "roe_sentences.csv", index=False)
    cat("ex21").to_csv(TABLES / "ratecase_subsidiary_check.csv", index=False)
    print(len(s), "sentences;", int(s["names_unit"].sum()), "name the unit")


if __name__ == "__main__":
    main()
