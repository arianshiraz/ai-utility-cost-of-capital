"""Select the rate-case unit for each US holding company (docs/ratecase_rule.md).

The unit is the (rate unit, state) pair with the largest 2023 electricity deliveries to ultimate
customers among the holding company's consolidated electric operating utilities. A rate unit is an
operating utility, or several sister utilities whose base rates are set in one proceeding
(column rate_unit in data/classification/us_operating_utilities.csv).
Deliveries are EIA-861 2023 totals across customer classes: bundled sales and delivery-only
service (Parts A, C and D of Sales_Ult_Cust, plus the Delivery_Companies file for Texas wires
utilities). Energy-only sales by retail marketers (Part B) are excluded.

Reads data/raw/eia861/f8612023.zip (downloaded from
https://www.eia.gov/electricity/data/eia861/archive/zip/f8612023.zip) and
data/classification/us_operating_utilities.csv. Writes output/tables/ratecase_units.csv (one
row per holding company) and output/tables/ratecase_unit_candidates.csv (every pair).
"""
import io
import zipfile
from pathlib import Path

import pandas as pd

from config import RAW, TABLES

CLS = Path(__file__).resolve().parents[1] / "data" / "classification"
ZIP = RAW / "eia861" / "f8612023.zip"
URL = "https://www.eia.gov/electricity/data/eia861/archive/zip/f8612023.zip"


def load(z: zipfile.ZipFile, name: str, sheet) -> pd.DataFrame:
    d = pd.read_excel(io.BytesIO(z.read(name)), sheet_name=sheet, header=2)
    d = d.rename(columns={"Megawatthours.4": "mwh_total", "Count.4": "customers_total"})
    return d


def main() -> None:
    if not ZIP.exists():
        import requests
        ZIP.parent.mkdir(parents=True, exist_ok=True)
        ZIP.write_bytes(requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=300).content)
    z = zipfile.ZipFile(ZIP)
    sales = load(z, "Sales_Ult_Cust_2023.xlsx", "States")
    sales = sales[sales["Part"].isin(["A", "C", "D"])]
    deliv = load(z, "Delivery_Companies_2023.xlsx", 0)
    d = pd.concat([sales, deliv], ignore_index=True)
    for c in ["mwh_total", "customers_total"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    pairs = (d.groupby(["Utility Number", "State"])
               .agg(mwh=("mwh_total", "sum"), customers=("customers_total", "sum"),
                    eia_name=("Utility Name", "first"))
               .reset_index())
    m = pd.read_csv(CLS / "us_operating_utilities.csv")
    c = m.merge(pairs, left_on="eia_utility_number", right_on="Utility Number", how="left")
    missing = c[c["mwh"].isna()]
    if len(missing):
        print("no EIA-861 2023 deliveries found for:", missing["operating_utility"].tolist())
    c = c.dropna(subset=["mwh"])
    c = (c.groupby(["ticker", "rate_unit", "State"], as_index=False)
           .agg(mwh=("mwh", "sum"), customers=("customers", "sum"),
                eia_utility_number=("eia_utility_number", lambda s: "; ".join(map(str, sorted(set(s))))),
                eia_name=("eia_name", lambda s: "; ".join(sorted(set(s))))))
    c = c.rename(columns={"rate_unit": "operating_utility"})
    c["share_of_holding_mwh"] = c["mwh"] / c.groupby("ticker")["mwh"].transform("sum")
    c = c.sort_values(["ticker", "mwh"], ascending=[True, False])
    cols = ["ticker", "operating_utility", "eia_utility_number", "eia_name", "State", "mwh",
            "customers", "share_of_holding_mwh"]
    TABLES.mkdir(parents=True, exist_ok=True)
    c[cols].to_csv(TABLES / "ratecase_unit_candidates.csv", index=False)
    top = c.groupby("ticker").head(2).copy()
    top["rank"] = top.groupby("ticker").cumcount() + 1
    first = top[top["rank"] == 1].set_index("ticker")
    second = top[top["rank"] == 2].set_index("ticker")
    out = first[cols[1:]].copy()
    out["runner_up"] = second["operating_utility"] + " (" + second["State"] + ")"
    out["runner_up_mwh"] = second["mwh"]
    out["margin_pct"] = ((out["mwh"] / out["runner_up_mwh"] - 1) * 100).round(1)
    out = out.reset_index().rename(columns={"State": "state"})
    out.to_csv(TABLES / "ratecase_units.csv", index=False)
    print(out[["ticker", "operating_utility", "state", "mwh", "share_of_holding_mwh",
               "runner_up", "margin_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
