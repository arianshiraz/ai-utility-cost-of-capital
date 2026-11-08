# Does the AI Boom Raise Utilities' Cost of Capital? Evidence across Regulatory Regimes

Regulators set the return that electricity networks may earn on equity, and customers pay it through their bills. Many regulators base that return partly on each utility's measured market risk (beta). This project tests whether the AI investment boom has raised utilities' co-movement with technology stocks and their measured beta, whether the rise is concentrated in utilities exposed to data-centre demand, and whether it has reached allowed returns, comparing regulators that use current market betas with those that fix beta or set returns by formula.

> **Status:** design frozen on 7 November 2026; first results for all four hypotheses on 8 November 2026 ([H1 and H2](docs/results_h1_h2.md), [H3 and H4](docs/results_h3_h4.md)); a short paper draft is in [`docs/paper.md`](docs/paper.md). Utilities with more data-centre exposure did not become more correlated with AI stocks; regulator-style betas fell in five of six countries; rebuilding regulators' betas shows an AI-era contribution of about +6 basis points for the UK and Spain and +22 to +35 for a German estimate made now, almost all through the market index rather than utilities' own exposure; US rate cases show no significant pass-through in the pre-specified model. The tests are fixed in [`docs/prespecification.md`](docs/prespecification.md), the exposure measure in [`docs/exposure_rule.md`](docs/exposure_rule.md) and the US rate-case sample in [`docs/ratecase_rule.md`](docs/ratecase_rule.md).

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
│   ├── 06_select_ratecase_units.py  # one US rate unit per holding company (EIA-861)
│   ├── 07_extract_ratecase_sentences.py # ROE sentences from 10-K and 10-Q filings (read in memory)
│   ├── 08_ratecase_candidates.py    # candidate decisions per unit (unverified reading aid)
│   ├── 10_ratecase_second_pass.py   # re-checks each coded decision against its source
│   ├── 11_rate_base_proxy.py        # FERC Form 1 net plant per US rate unit (H4)
│   ├── 12_returns.py                # daily and weekly returns and factors
│   ├── 13_placebo_exposure.py       # FY2023 exposure for US water and gas placebos
│   ├── 14_h1_comovement.py          # H1 tests, placebo breaks, robustness
│   ├── 15_h2_decomposition.py       # H2 beta decomposition
│   ├── 16_figures.R                 # figures (tidyplots, ggdist)
│   ├── 17_h3_replicas.py            # UK, Germany, Spain replicas and counterfactuals
│   ├── 18_h3_us_panel.py            # US rate-case panel and H4
│   ├── 19_h3_robustness.py          # H3 robustness checks
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

Stages 02, 03 and 07 read SEC filings (stage 07 reads them in memory and keeps only the extracted sentences), and SEC requires a contact in each request: set the environment variable `SEC_USER_AGENT` (for example "Your Name your@email") first. Without it, `run_all.py` skips those stages and reuses the committed tables. Every dataset gathered so far is documented, with sources, in `data/project_data_workbook.xlsx`.

## Author and license

Arian Nasrollahi Shiraz. A research project on electricity regulation and finance. It is a research artifact, not a peer-reviewed publication.

Code is released under the [MIT License](LICENSE). Downloaded data are not redistributed and remain subject to their providers' terms.
