"""Rate-base proxy and customers for each US rate unit (input to H4: basis points into dollars).

Source: FERC Form 1, schedule 200 (summary of utility plant), net electric utility plant at year end,
as cleaned by the Public Utility Data Liberation project (PUDL, Catalyst Cooperative, CC-BY-4.0):
https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/out_ferc1__yearly_utility_plant_summary_sched200.parquet
(downloaded to data/raw/pudl/).

Net electric plant is a proxy for rate base: rate base also deducts accumulated deferred income
taxes and adds working capital, and net plant includes FERC-jurisdictional transmission. For rate
units that serve several states, net plant is scaled by the unit's share of the operating utility's
2023 deliveries in the rate-case state (EIA-861, output/tables/ratecase_unit_candidates.csv).
Texas-New Mexico Power stopped filing FERC Form 1 after 2006; its value is the rate base stated in
its 2025 rate filing (TXNM 10-K filed 27 February 2026), flagged in the output.
Customers are 2023 ultimate customers of the rate unit in its state (EIA-861).
Output: output/tables/ratecase_rate_base_proxy.csv (unit by year, 2015 onward).
"""
from pathlib import Path

import pandas as pd
import requests

from config import RAW, TABLES

URL = ("https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/"
       "out_ferc1__yearly_utility_plant_summary_sched200.parquet")
FILE = RAW / "pudl" / "out_ferc1__yearly_utility_plant_summary_sched200.parquet"
FERC_IDS = {  # rate unit -> FERC Form 1 respondent ids (utility_id_ferc1)
    "AEE": [222], "AEP": [204], "AVA": [182], "BKH": [289], "CMS": [163], "CNP": [318], "D": [164],
    "DTE": [184], "DUK": [170], "ED": [159], "EIX": [155], "ES": [271], "ETR": [362], "EVRG": [225, 356],
    "EXC": [165], "FE": [174, 175, 176], "IDA": [216], "LNT": [220], "MGEE": [335], "NEE": [247],
    "NI": [208], "NWE": [315], "OGE": [314], "OTTR": [272], "PCG": [183], "PNW": [286], "POR": [250],
    "PPL": [267], "SO": [295], "SRE": [218], "WEC": [280], "XEL": [229],
}
TXNM_RATE_BASE = {"year": 2025, "value": 2.8e9,
                  "source": "TXNM 10-K filed 2026-02-27: TNMP Base Rate Review requesting recovery of $2.8 billion of rate base as of June 30, 2025 (requested, not approved)"}


def main() -> None:
    if not FILE.exists():
        FILE.parent.mkdir(parents=True, exist_ok=True)
        FILE.write_bytes(requests.get(URL, timeout=300).content)
    d = pd.read_parquet(FILE)
    d = d[(d.utility_type == "electric") & (d.utility_plant_asset_type == "utility_plant_net")
          & (d.report_year >= 2015)]
    units = pd.read_csv(TABLES / "ratecase_units.csv")
    cand = pd.read_csv(TABLES / "ratecase_unit_candidates.csv")
    rows = []
    for _, u in units.iterrows():
        t = u.ticker
        # state share of the rate unit's operating utilities' deliveries
        ops = cand[(cand.ticker == t) & (cand.operating_utility == u.operating_utility)]
        same = ops[ops.State == u.state]
        share = float(same.mwh.sum() / ops.mwh.sum()) if len(same) and ops.mwh.sum() else 1.0
        if t == "TXNM":
            rows.append({"ticker": t, "rate_unit": u.operating_utility, "state": u.state,
                         "year": TXNM_RATE_BASE["year"], "net_electric_plant": "", "state_share": "",
                         "rate_base_proxy": TXNM_RATE_BASE["value"], "customers_2023": u.customers,
                         "source": TXNM_RATE_BASE["source"]})
            continue
        s = d[d.utility_id_ferc1.isin(FERC_IDS[t])].groupby("report_year").ending_balance.sum()
        for y, v in s.items():
            rows.append({"ticker": t, "rate_unit": u.operating_utility, "state": u.state, "year": int(y),
                         "net_electric_plant": v, "state_share": round(share, 4),
                         "rate_base_proxy": v * share, "customers_2023": u.customers,
                         "source": f"FERC Form 1 sched. 200 via PUDL, respondents {FERC_IDS[t]}"})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "ratecase_rate_base_proxy.csv", index=False)
    last = out.sort_values("year").groupby("ticker").tail(1)
    print(last[["ticker", "year", "state_share", "rate_base_proxy", "customers_2023"]].assign(
        rate_base_bn=lambda x: (x.rate_base_proxy / 1e9).round(1)).drop(columns="rate_base_proxy").to_string(index=False))


if __name__ == "__main__":
    main()
