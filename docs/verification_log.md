# Verification of citations and claims

Checked on 8 November 2026, before the repository was made public. Each item below was compared with its source; corrections are listed at the end.

## Literature cited in the paper

| Reference | Checked against | Result |
|---|---|---|
| Blume (1971), *Journal of Finance* 26(1), 1 to 10 | AFA issue listing | Confirmed |
| Diebold and Yilmaz (2012), *International Journal of Forecasting* 28(1), 57 to 66 | Journal record (7 November 2026) | Confirmed |
| Dunkle Werner and Jarvis (2026), *Journal of Public Economics* 259, 105654 | LSE Research Online record and published abstract | Confirmed; the paper now cites the journal version, whose abstract gives excess costs averaging $7 billion a year |
| Hamada (1972), *Journal of Finance* 27(2), 435 to 452 | Bibliographic records | Confirmed |
| Harris and Pringle (1985), *Journal of Financial Research* 8(3), 237 to 244 | RePEc/IDEAS | Confirmed |
| Nasrollahi Shiraz (2026), DeepSeek event study | Public repository README | Figures (−19%, 20.5 points) confirmed |
| Rode and Fischbeck (2019), *Energy Policy* 133, 110891 | RePEc/IDEAS abstract | Confirmed; wording corrected to the abstract's claim (a large and growing premium over the riskless rate across nearly four decades) |
| Roll (1977), *Journal of Financial Economics* 4(2), 129 to 176 | EconPapers | Confirmed |
| Van Nieuwerburgh (2026), BPEA conference draft | Text read (7 November 2026) | Confirmed |
| Vasicek (1973), *Journal of Finance* 28(5), 1233 to 1239 | EconPapers | Confirmed |
| Webb (2023), *Canadian Journal of Economics* 56(3), 839 to 858 | RePEc | Confirmed |

## Regulatory facts (primary documents read in memory, page as printed in the PDF viewer)

| Claim | Source | Result |
|---|---|---|
| RIIO-3: asset beta 0.375 chosen as the midpoint of 0.30 to 0.45; debt beta 0.075; notional gearing 55% (electricity), 60% (gas) | Ofgem RIIO-3 Final Determinations Finance Annex, pp54 to 55 | Confirmed |
| RIIO-3: risk-free rate 2.30%, total market return 6.9% (premium 4.6%), CPIH-real | Same, p45 | Confirmed |
| RIIO-2: asset beta 0.349 (range 0.323 to 0.373) | RIIO-2 Final Determinations Finance Annex (revised), pp24, 40 | Confirmed |
| CNMC: 34 comparators; 6 years of weekly data; gearing 46%; equity beta 0.75 (0.72 before); premium 4.98%; return on equity 7.00%; remuneration rate 6.58% | CNMC, explanatory memo of Circular 9/2025 (6336126.pdf), pp75, 104, 106, 109 to 110, 117 to 119, 145 | Confirmed; the stored link pointed to a different CNMC document and was corrected |
| BNetzA: market risk premium 3.7%; Vasicek adjustment | BK4-21-0055, pp13, 17, 27, 32 | Confirmed |
| Germany: 40% notional equity share | §7(1) StromNEV | Confirmed; the source was added to the parameter file |
| ARERA: asset betas 0.370 (transmission), 0.400 (distribution), unchanged for 2025 to 2027; Blume "anche solo parziale", daily data, Hamada with book equity | Delibera 614/2021 p16; Delibera 513/2024 pp4, 6 to 7 | Confirmed |
| Value Line beta: 5 years of weekly changes against the NYSE Composite, adjusted toward 1 with about two-thirds weight on the raw beta | Columbia Gas of Kentucky, response to AG 1-98, Kentucky PSC Case 2007-00008 (secondary) | Confirmed from a secondary source; the paper's description was corrected (it had not named the index) |

## Numbers in the paper and README

Every number in `docs/paper.md` and `README.md` was compared with the output tables (`output/tables/`). Corrections: regulated utilities' AI loading is −0.28 before 2023 and −0.27 after (previously "−0.27 in both periods"); the US exposure channel averages −0.001 (previously −0.002); the rate-base proxy ratio of 1.2 to 2.7 covers five units.

## What remains secondary or unverified

- Canadian formula parameters (OEB and AUC websites refuse automated requests).
- The median US authorised return of about 9.70% in 2025 (industry compilation; not used in any estimate).
- Value Line's method rests on a utility's quotation of Value Line, not on Value Line's own documentation.
- The US replica uses the S&P 500, not Value Line's NYSE Composite; the paper states this as a limitation.
