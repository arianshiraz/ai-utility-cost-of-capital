"""Machine-extracted candidate rate-case decisions, one row per unit and ROE value (unverified).

Reads output/tables/roe_sentences.csv. For each rate unit, keeps sentences that name the unit's
state or commission (in the sentence or the sentence before), states a return on equity between
6% and 13%, and are not about FERC transmission, gas service, pensions or earnings sharing.
Each sentence is classed as an authorised value ("auth": approved, authorised, ordered, settled,
allowed) or a requested value ("req": requested, proposed, recommended by staff or intervenors).
Rows with the same unit, class and ROE value are merged; the first and last filing that mention
the value, the equity ratios and the month-year phrases found nearby are kept, with one quote and
its filing URL.

These candidates are a reading aid. Only values checked by hand and entered in
data/classification/ratecase_decisions.csv enter the analysis (docs/ratecase_rule.md).
Output: output/tables/ratecase_candidates.csv
"""
import re

import pandas as pd

from config import TABLES

UNIT_STATE = {
    "AEE": r"Ameren Illinois|\bICC\b|Illinois", "AEP": r"\bOhio\b|OPCo|PUCO", "AVA": r"Washington|\bUTC\b|WUTC",
    "BKH": r"Cheyenne|Wyoming|WPSC", "CMS": r"Consumers|MPSC|Michigan", "CNP": r"Houston|PUCT|Texas",
    "D": r"Virginia|\bSCC\b", "DTE": r"DTE Electric|MPSC|Michigan", "DUK": r"Duke Energy Carolinas|NCUC|North Carolina",
    "ED": r"CECONY|NYSPSC|NYPSC|New York", "EIX": r"\bSCE\b|CPUC|cost of capital", "ES": r"NSTAR Electric|\bDPU\b|Massachusetts",
    "ETR": r"Entergy Louisiana|LPSC|Louisiana", "EVRG": r"Kansas Central|Westar|\bKCC\b|Kansas", "EXC": r"ComEd|\bICC\b|Illinois",
    "FE": r"Ohio Companies|PUCO|\bOhio\b", "IDA": r"Idaho Power|IPUC|Idaho", "LNT": r"\bIPL\b|\bIUB\b|Iowa",
    "MGEE": r"\bMGE\b|PSCW|Wisconsin", "NEE": r"\bFPL\b|FPSC|Florida", "NI": r"NIPSCO|IURC|Indiana",
    "NWE": r"Montana|MPSC", "OGE": r"OG&E|\bOCC\b|Oklahoma", "OTTR": r"Minnesota|MPUC",
    "PCG": r"CPUC|cost of capital", "PNW": r"\bAPS\b|\bACC\b|Arizona", "POR": r"OPUC|Oregon|\bPGE\b",
    "PPL": r"PPL Electric|\bPUC\b|Pennsylvania", "SO": r"Georgia Power|Georgia PSC", "SRE": r"SDG&E|CPUC|cost of capital",
    "TXNM": r"TNMP|PUCT|Texas", "WEC": r"Wisconsin Electric|We Energies|PSCW", "XEL": r"NSP-Minnesota|MPUC|Minnesota",
}
SKIP = re.compile(r"FERC|MISO|ISO-NE|PJM|natural gas|gas rate|gas distribution|gas utility|transmission formula|"
                  r"pension|plan assets|earnings sharing|earned|exceed", re.I)
N = r"(\d{1,2}\.\d{1,3})\s?(?:%|percent)"
ROE1 = re.compile(r"(?:ROE|return on (?:common )?equity)[^.;]{0,70}?" + N, re.I)
ROE2 = re.compile(N + r"[^.;]{0,25}?(?:ROE|return on (?:common )?equity)", re.I)
EQ = re.compile(r"(?:equity ratio|common equity(?: ratio)?|equity component|equity layer)[^.;]{0,25}?(\d{2}(?:\.\d{1,2})?)"
                r"\s?(?:%|percent)|(\d{2}(?:\.\d{1,2})?)\s?(?:%|percent)[^.;]{0,15}(?:common )?equity", re.I)
DATE = re.compile(r"(?:In|On|in|on)\s+((?:January|February|March|April|May|June|July|August|September|October|"
                  r"November|December)(?:\s+\d{1,2},)?\s+\d{4})")
REQ = re.compile(r"request|propos|seek|sought|filed|recommend|testimony|intervenor|staff|asking|applied for", re.I)
AUT = re.compile(r"approv|authori[sz]ed|allowed|order|settle|stipulat|granted|final|adopt|decision|currently|based on", re.I)


def main() -> None:
    d = pd.read_csv(TABLES / "roe_sentences.csv").drop_duplicates(["ticker", "filing_date", "sentence"])
    rows = []
    for _, r in d.iterrows():
        st = re.compile(UNIT_STATE[r.ticker], re.I)
        s, c = str(r.sentence), str(r.context)
        if SKIP.search(s) or not (st.search(s) or st.search(c[-250:])):
            continue
        m = ROE1.search(s) or ROE2.search(s)
        if not m or not 6 <= float(m.group(1)) <= 13:
            continue
        e = EQ.search(s)
        dates = DATE.findall(s) or DATE.findall(c[-250:])
        kind = ("req" if REQ.search(s) and not re.search(r"approv|authori[sz]ed|order", s, re.I)
                else ("auth" if AUT.search(s) else "other"))
        if kind == "other":
            continue
        rows.append({"ticker": r.ticker, "kind": kind, "roe_pct": float(m.group(1)),
                     "equity_pct": (e.group(1) or e.group(2)) if e else "", "date_phrase": dates[-1] if dates else "",
                     "filing_date": r.filing_date, "url": r.url, "quote": re.sub(r"\s+", " ", s)[:400]})
    c = pd.DataFrame(rows).sort_values(["ticker", "filing_date"])
    out = (c.groupby(["ticker", "kind", "roe_pct"], sort=False)
             .agg(first_filing=("filing_date", "first"), last_filing=("filing_date", "last"),
                  mentions=("quote", "size"),
                  equity_pct=("equity_pct", lambda x: "; ".join(sorted(set(v for v in x if v)))),
                  date_phrases=("date_phrase", lambda x: "; ".join(sorted(set(v for v in x if v)))),
                  quote=("quote", "first"), url=("url", "first"))
             .reset_index().sort_values(["ticker", "first_filing", "kind"]))
    out.insert(0, "status", "unverified")
    out.to_csv(TABLES / "ratecase_candidates.csv", index=False)
    print(len(out), "candidate rows;", (out.kind == "auth").sum(), "authorised;",
          out.ticker.nunique(), "units")
    print(out[out.kind == "auth"].groupby("ticker").size().to_string())


if __name__ == "__main__":
    main()
