# Does the AI Boom Raise Utilities' Cost of Capital? Evidence across Regulatory Regimes

Regulators set the return that electricity networks may earn on equity, and customers pay it through their bills. Many regulators base that return partly on each utility's measured market risk (beta). This project tests whether the AI investment boom has raised utilities' co-movement with technology stocks and their measured beta, whether the rise is concentrated in utilities exposed to data-centre demand, and whether it has reached allowed returns, comparing regulators that use current market betas with those that fix beta or set returns by formula.

> **Status:** design frozen on 7 November 2026. Price data for 80 series across eight countries is downloaded and checked for coverage; no returns have been analysed. The design and hypotheses are in [`docs/research_design.md`](docs/research_design.md); the tests are fixed in [`docs/prespecification.md`](docs/prespecification.md) and the exposure measure in [`docs/exposure_rule.md`](docs/exposure_rule.md).

## Repository layout

```
.
├── run_all.py
├── code/
│   ├── config.py                    # dates, market indices, AI factors, FX
│   ├── 01_download_prices.py
│   ├── 02_collect_dc_disclosures.py # SEC filings mentioning data centres
│   ├── 03_dc_exposure_measures.py   # exposure measures, FY2023 and FY2024
│   ├── 05_download_rates.py         # national 10-year government bond yields
│   └── 09_build_workbook.py         # documented Excel workbook of all data
├── data/
│   ├── project_data_workbook.xlsx   # every dataset gathered, with sources
│   ├── classification/              # utilities, regulator methods and parameters
│   ├── raw/                         # downloads (not committed)
│   └── derived/
├── output/{tables,figures}/
└── docs/research_design.md
```

## Reproducing

Requires Python 3.10 or later. Figures will use R with `tidyplots` and `ggdist`.

```bash
pip install -r requirements.txt
python run_all.py
```

Stages 02 and 03 download SEC filings, and SEC requires a contact in each request: set the environment variable `SEC_USER_AGENT` (for example "Your Name your@email") first. Without it, `run_all.py` skips those stages and reuses the committed tables. Every dataset gathered so far is documented, with sources, in `data/project_data_workbook.xlsx`.

## Author and license

Arian Nasrollahi Shiraz. A research project on electricity regulation and finance. It is a research artifact, not a peer-reviewed publication.

Code is released under the [MIT License](LICENSE). Downloaded data are not redistributed and remain subject to their providers' terms.
