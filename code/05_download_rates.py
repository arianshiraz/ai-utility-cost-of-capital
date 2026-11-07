"""Download national 10-year government bond yields (the rate factor in every model).

Pre-specification, section 1: daily change in the national 10-year government bond yield,
from the national central bank or an official statistical source.

Writes the files exactly as downloaded to data/raw/rates/, a tidy daily panel to
data/derived/yields_daily.csv (country, date, yield in percent, series) and a coverage
table to output/tables/yields_coverage.csv.

Italy (pre-specification, Amendment 1): the Bank of Italy publishes the 10-year BTP benchmark
yield only monthly (Infostat MFN_BMK.M.020.922.0.EUR.210), and no official daily national series
was found. The main Italian series is the ECB daily euro-area 10-year yield on all government
bonds (IT_EA_ALL); the German series is the robustness check; the ECB monthly Italian yield
(IT_MONTHLY) is kept for checking only.
"""
import io
import json
from datetime import datetime, timezone

import pandas as pd
import requests

from config import DERIVED, RAW, START, TABLES

UA = {"User-Agent": "curl/8.4.0"}  # FRED rejects browser-style agents
OUT = RAW / "rates"

SOURCES = {
    "US": ("FRED DGS10, 10-year Treasury constant maturity",
           "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10", "us_fred_dgs10.csv"),
    "UK": ("Bank of England IUDMNPY, 10-year nominal par yield",
           "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes"
           "&Datefrom=01/Jan/2012&Dateto=now&SeriesCodes=IUDMNPY&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N",
           "uk_boe_iudmnpy.csv"),
    "DE": ("Bundesbank BBSIS, Svensson term structure, 10-year residual maturity",
           "https://api.statistiken.bundesbank.de/rest/data/BBSIS/"
           "D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?format=csv&lang=en&startPeriod=2012-01-01",
           "de_bbk_svensson10y.csv"),
    "ES": ("Banco de Espana DPUG0B1F0ZP, 10-year state bonds, secondary market (summary indicators)",
           "https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/uoi_sindi.csv",
           "es_bde_uoi_sindi.csv"),
    "CA": ("Bank of Canada BD.CDN.10YR.DQ.YLD, 10-year benchmark bond yield",
           "https://www.bankofcanada.ca/valet/observations/BD.CDN.10YR.DQ.YLD/csv?start_date=2012-01-01",
           "ca_boc_10y.csv"),
    "IT_EA_ALL": ("ECB YC, euro-area 10-year spot yield, all government bonds (Italy, Amendment 1)",
                  "https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_C.SV_C_YM.SR_10Y"
                  "?startPeriod=2012-01-01&format=csvdata", "ecb_yc_ea_all_10y.csv"),
    "IT_MONTHLY": ("ECB IRS, Italy long-term (10-year) convergence yield, monthly (check only)",
                   "https://data-api.ecb.europa.eu/service/data/IRS/M.IT.L.L40.CI.0000.EUR.N.Z"
                   "?startPeriod=2012-01&format=csvdata", "ecb_irs_it_monthly.csv"),
    "US_BAA10Y": ("FRED BAA10Y, Moody's seasoned Baa corporate yield minus 10-year Treasury (spread control, Amendment 3)",
                  "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAA10Y", "us_fred_baa10y.csv"),
}

ES_MONTHS = {"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AGO": 8,
             "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12}


def parse(key: str, raw: bytes) -> pd.Series:
    if key in ("US", "US_BAA10Y"):
        d = pd.read_csv(io.BytesIO(raw), na_values=".")
        return pd.Series(d.iloc[:, 1].values, index=pd.to_datetime(d.iloc[:, 0]))
    if key == "UK":
        d = pd.read_csv(io.BytesIO(raw))
        return pd.Series(d["IUDMNPY"].values, index=pd.to_datetime(d["DATE"], format="%d %b %Y"))
    if key == "DE":
        d = pd.read_csv(io.BytesIO(raw), skiprows=9, header=None, encoding="utf-8-sig",
                        na_values=["."])
        d = d[d[0].astype(str).str.match(r"\d{4}-\d{2}-\d{2}")]
        return pd.Series(pd.to_numeric(d[1], errors="coerce").values, index=pd.to_datetime(d[0]))
    if key == "ES":
        d = pd.read_csv(io.BytesIO(raw), encoding="latin-1", header=None, dtype=str)
        col = d.iloc[0].tolist().index("DPUG0B1F0ZP")
        body = d.iloc[6:]
        dates = body[0].str.split(" ").apply(
            lambda p: pd.Timestamp(int(p[2]), ES_MONTHS[p[1]], int(p[0])))
        return pd.Series(pd.to_numeric(body[col], errors="coerce").values, index=dates.values)
    if key == "CA":
        text = raw.decode("utf-8")
        start = text.index('"date"')
        d = pd.read_csv(io.StringIO(text[start:]))
        return pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values,
                         index=pd.to_datetime(d["date"]))
    d = pd.read_csv(io.BytesIO(raw))
    idx = pd.PeriodIndex(d["TIME_PERIOD"], freq="M").to_timestamp(how="end").normalize() \
        if key == "IT_MONTHLY" else pd.to_datetime(d["TIME_PERIOD"])
    return pd.Series(d["OBS_VALUE"].values, index=idx)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames, meta = [], {}
    for key, (label, url, fname) in SOURCES.items():
        r = requests.get(url, headers=UA, timeout=120)
        r.raise_for_status()
        (OUT / fname).write_bytes(r.content)
        s = parse(key, r.content).dropna().sort_index()
        s = s[s.index >= START]
        frames.append(pd.DataFrame({"country": key, "date": s.index.date, "yield_pct": s.values,
                                    "series": label}))
        meta[key] = {"series": label, "url": url, "file": fname}
        print(f"{key:10s} {len(s):5d} obs  {s.index.min().date()} to {s.index.max().date()}")
    panel = pd.concat(frames, ignore_index=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    panel.to_csv(DERIVED / "yields_daily.csv", index=False)
    cov = panel.groupby(["country", "series"]).agg(first=("date", "min"), last=("date", "max"),
                                                   n_obs=("yield_pct", "size"),
                                                   mean_pct=("yield_pct", "mean")).reset_index()
    cov["mean_pct"] = cov["mean_pct"].round(3)
    TABLES.mkdir(parents=True, exist_ok=True)
    cov.to_csv(TABLES / "yields_coverage.csv", index=False)
    meta["downloaded_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (OUT / "rates_meta.json").write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
