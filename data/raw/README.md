# Raw data provenance

Nothing in this folder is committed except this file. code/01_download_prices.py recreates it.

| File | Source | Notes |
|---|---|---|
| prices_yf.csv | Yahoo Finance via yfinance, daily adjusted close, 2012 to 2026 | Download time in download_meta.json. Re-downloaded 7 Nov 2026 to add the FTSE All-Share (^FTAS) |
| rates/us_fred_dgs10.csv | FRED, series DGS10, https://fred.stlouisfed.org/series/DGS10 | Downloaded 7 Nov 2026 by code/05_download_rates.py |
| rates/uk_boe_iudmnpy.csv | Bank of England database, series IUDMNPY (10-year nominal par yield) | Downloaded 7 Nov 2026 |
| rates/de_bbk_svensson10y.csv | Bundesbank API, BBSIS.D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A | Downloaded 7 Nov 2026 |
| rates/es_bde_uoi_sindi.csv | Banco de Espana summary indicators (uoi_sindi.csv); column DPUG0B1F0ZP | Downloaded 7 Nov 2026; Latin-1 encoding, Spanish month names |
| rates/ca_boc_10y.csv | Bank of Canada Valet API, BD.CDN.10YR.DQ.YLD | Downloaded 7 Nov 2026 |
| rates/ecb_yc_ea_all_10y.csv | ECB Data Portal, YC.B.U2.EUR.4F.G_N_C.SV_C_YM.SR_10Y (euro area, all government bonds) | Candidate rate factor for Italy, pending decision |
| rates/ecb_irs_it_monthly.csv | ECB Data Portal, IRS.M.IT.L.L40.CI.0000.EUR.N.Z (Italy, monthly) | For checking the Italian candidate only |
| rates/rates_meta.json | URLs and download time | |
| rates/us_fred_baa10y.csv | FRED BAA10Y (Moody's Baa corporate yield minus 10-year Treasury) | Downloaded 8 Nov 2026 by code/05_download_rates.py; spread control under Amendment 3 |
| pudl/out_ferc1__yearly_utility_plant_summary_sched200.parquet | FERC Form 1 schedule 200 via PUDL (Catalyst Cooperative, CC-BY-4.0), https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/out_ferc1__yearly_utility_plant_summary_sched200.parquet | Downloaded 8 Nov 2026; used by code/11_rate_base_proxy.py |
| eia861/f8612023.zip | EIA-861 2023, https://www.eia.gov/electricity/data/eia861/archive/zip/f8612023.zip | Downloaded 7 Nov 2026; Sales_Ult_Cust and Delivery_Companies files used by code/06_select_ratecase_units.py |
