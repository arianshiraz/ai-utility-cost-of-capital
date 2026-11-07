"""Second pass on the hand-coded rate-case decisions (docs/ratecase_rule.md).

For every row of data/classification/ratecase_decisions.csv that has a source URL, the source is
read again in memory and four checks are made:
  quote_found      share of the quoted fragments (split at "...") found verbatim in the source
  roe_found        the recorded authorised ROE appears in the source as a percentage
  roe_near_month   the ROE appears within 1,500 characters of the order month ("Month YYYY")
  equity_found     the recorded equity ratio appears in the source as a percentage (if recorded)
A row passes when the ROE is found near the order month (or, for rows without an ROE, when the
quote is found). Rows that fail are listed for review by hand; the review outcome is written to the
second_pass column of the decisions file, not by this script.
Output: output/tables/ratecase_second_pass.csv. SEC requires a contact: set SEC_USER_AGENT.
"""
import html
import importlib.util
import re
from pathlib import Path

import pandas as pd
import requests

from config import TABLES

_spec = importlib.util.spec_from_file_location(
    "collect", Path(__file__).with_name("02_collect_dc_disclosures.py"))
collect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(collect)

CLS = Path(__file__).resolve().parents[1] / "data" / "classification"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]


def to_text(raw: bytes, url: str) -> str:
    if url.lower().endswith(".pdf"):
        import fitz
        return " ".join(p.get_text() for p in fitz.open(stream=raw, filetype="pdf"))
    s = raw.decode("utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return html.unescape(s)


def norm(s: str) -> str:
    s = s.replace("‑", " ").replace("‐", " ").replace("’", "'").replace("–", "-")
    s = re.sub(r"\s+", " ", s)
    return re.sub(r"\s+([%,.;])", r"\1", s).lower()


def pct_pattern(v: str) -> str:
    x = float(v)
    forms = {f"{x:g}", f"{x:.2f}", f"{x:.1f}", f"{x:.3f}"}
    alt = "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True))
    return rf"(?<![\d.])(?:{alt})\s?(?:%|percent| percent|-percent)"


def main() -> None:
    d = pd.read_csv(CLS / "ratecase_decisions.csv", dtype=str).fillna("")
    cache, rows = {}, []
    for i, r in d.iterrows():
        u = r.source_url
        if not u:
            rows.append({"row": i, "ticker": r.ticker, "order_date": r.order_date, "status": "no source"})
            continue
        if u not in cache:
            try:
                raw = collect.get(u) if "sec.gov" in u else requests.get(
                    u, headers={"User-Agent": "Mozilla/5.0"}, timeout=90).content
                cache[u] = norm(to_text(raw, u))
            except Exception as e:  # noqa: BLE001
                cache[u] = ""
                print("fetch failed", u, type(e).__name__)
        t = cache[u]
        frags = [norm(x).strip(" .()") for x in re.split(r"\.\.\.|\(10-K|\(10-Q|\(request|\(ROE|\(rate", r.quote)]
        frags = [x for x in frags if len(x) >= 25]
        q = sum(1 for x in frags if x[:80] in t) / len(frags) if frags else 0.0
        roe_found = roe_near = eq_found = ""
        if r.roe_authorised_pct:
            hits = [m.start() for m in re.finditer(pct_pattern(r.roe_authorised_pct), t)]
            roe_found = int(bool(hits))
            ym = re.match(r"(\d{4})-(\d{2})", r.order_date)
            if ym and hits:
                mon = MONTHS[int(ym.group(2)) - 1].lower() + r"(?: \d{1,2},)? " + ym.group(1)
                mpos = [m.start() for m in re.finditer(mon, t)]
                roe_near = int(any(abs(h - m) <= 1500 for h in hits for m in mpos))
            elif hits:
                roe_near = ""
        if r.equity_ratio_pct:
            eq_found = int(bool(re.search(pct_pattern(r.equity_ratio_pct), t)))
        if not t:
            status = "fetch failed"
        elif r.roe_authorised_pct:
            status = "pass" if roe_near == 1 or (roe_near == "" and roe_found == 1 and q >= 0.5) else "review"
        else:
            status = "pass" if q >= 0.5 else "review"
        rows.append({"row": i, "ticker": r.ticker, "order_date": r.order_date, "in_panel": r.in_panel,
                     "roe": r.roe_authorised_pct, "quote_found": round(q, 2), "roe_found": roe_found,
                     "roe_near_month": roe_near, "equity_found": eq_found, "status": status})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "ratecase_second_pass.csv", index=False)
    print(out.status.value_counts().to_string())
    print(out[out.status != "pass"].to_string(index=False))


if __name__ == "__main__":
    main()
