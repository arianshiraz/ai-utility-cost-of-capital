# How each regulator sets the return on equity (decision D2)

**Purpose.** Record, from each regulator's own decision documents, exactly how it estimates beta and the allowed return on equity. Hypothesis H3 depends on this: pass-through of AI-driven beta changes is only possible where current market betas enter the allowed return.

**Evidence levels.** The findings table gives a page for every value read in a regulator's own document. Notes under "Sources" that carry no page come from secondary sources found on 7 November 2026 and are still to be checked against the primary documents.

**Timing matters.** Several determinations were made inside the AI era (after November 2022) using beta windows that include 2023 to 2025. Those are the observations that can test pass-through outside the US.

---

## Findings (extracted 7 November 2026)

"Primary" means read in the regulator's own document, with the page given. "Secondary" means from summaries or search results, still to confirm.

| Field | US | UK (Ofgem) | Germany (BNetzA) | Spain (CNMC) | Italy (ARERA) | Canada (OEB, AUC) |
|---|---|---|---|---|---|---|
| Decision used | State rate cases; FERC Opinion 569 line for transmission | RIIO-3 Final Determinations, Dec 2025 (2026 to 2031) | BK4-21-0055, 12 Oct 2021 (electricity distribution, 2024 to 2028) | Circular 9/2025 explanatory memo, Dec 2025 (2026 to 2031) | Delibera 513/2024/R/com, 28 Nov 2024 (2025 to 2027) | OEB EB-2024-0063, 27 Mar 2025; AUC 27084-D02-2023 |
| CAPM role | One of several models (DCF, CAPM, risk premium) argued case by case (secondary) | CAPM is step 1; cross-checks support the midpoint (primary, p45, p59) | CAPM (primary, p11 to 12) | WACC with CAPM cost of equity (primary, p15, p75) | WACC with CAPM (primary) | None: formula on bond yields and utility bond spreads (secondary) |
| Beta source | Proxy groups of US utilities; Value Line betas common (secondary) | Nine comparators weighted equally: UU, Severn Trent, Pennon, National Grid, Enagás, Snam, Redeia, Terna, Italgas (primary, FD p58; DD p56 Table 16) | Listed foreign network operators with over 75% network business; Euro Stoxx or FTSE All-World sub-indices (primary, p25 to 27, p30, p37); the comparator table is missing from the accessible PDF (p36) | 34 European comparators from STOXX and Bloomberg (primary, p75, p106) | Comparator firms in similar sectors and regions; regulated revenue at least 20%; liquidity filter (primary, p4) | Not applicable |
| Window | Value Line: 5 years (secondary, to verify) | 10-year asset betas; 2- and 5-year shown (primary, FD p55; DD p56) | 1, 3 and 5 years, with more weight on 1 year (2020); over 5 years rejected (primary, p36 to 37) | 6 years, data to 31 December 2023 (primary, p75, p143) | 5 years (2019 to 2023), compared with 2022 to 2023 (primary, p4) | Not applicable |
| Frequency | Value Line: weekly (secondary, to verify) | Daily, OLS, most diversified local index (primary, p56) | Daily; weekly and monthly rejected (primary, p31) | Weekly, Bloomberg regression (primary, p75) | Daily, national index of each country (primary, p4) | Not applicable |
| Adjustment | Blume (Value Line) (secondary) | None to the beta; range 0.30 to 0.45, midpoint chosen (primary, p55) | Vasicek (primary, p27, p32) | None; comparators with a bid-ask spread above 1% excluded (primary, p75 to 76) | Blume, possibly partial (primary, p4) | Not applicable |
| Debt beta and gearing | Case by case | Debt beta 0.075; gearing 55% (electricity), 60% (gas) (primary, p55) | Tax and capital-structure adjustment (primary, p25) | No debt beta; Modigliani-Miller unlevering, Hamada re-levering; gearing 46%, down from 50% (primary, pp76 to 77, p109) | Hamada with book equity (primary, p4) | Not applicable |
| Resulting values | Median authorised electric return about 9.70% (2025, secondary) | Asset beta 0.375; equity beta 0.74 (electricity), 0.83 (gas); cost of equity 5.70% and 6.12% CPIH-real (primary, p45) | Risk factor 0.81; 5.07% new assets, 3.51% old, pre-tax (primary, p25; secondary) | Asset beta 0.46; equity beta 0.75 (0.72 in 2020 to 2025); return on equity 7.00%; remuneration rate 6.58% (primary, pp114 to 119, p145) | Asset beta for 2025 to 2027: 0.370 transmission, 0.400 distribution; WACC 2025: 5.5% and 5.6% (primary, pp6 to 7) | Ontario 2026: 9.11%; Alberta 2024: 9.28% (secondary) |
| Re-estimated | Each rate case, typically every 2 to 4 years | Every 5 years; only the risk-free rate is updated annually and the equity return indexed to it (primary, p45) | Every 5 years; next electricity period from 2029, method set Dec 2025 | Every 6 years | 3-year sub-periods | Annually by formula; base reviewed every few years |
| Regime for H3 | Fast pass-through | Slow and damped | Very sensitive to recent betas, but the current values use 2020 and stay fixed until 2029 | Low: one AI-era year (2023) in a 6-year window, fixed until 2031 | Medium, mostly pre-AI window | No pass-through |

---

## Additions (8 November 2026)

- **UK, previous period.** RIIO-2 Final Determinations (December 2020, revised February 2021) set an asset beta of 0.349 (range 0.323 to 0.373), a debt beta of 0.075 and a notional equity beta of 0.759, with a 6.5% total market return (primary, Finance Annex pp24, 40). RIIO-3 set 0.375, so the UK asset beta rose by 0.026 between a determination estimated on pre-AI data and one estimated on windows that include 2023 to 2025.
- **Italy, previous period.** Delibera 614/2021 (23 December 2021) set asset betas for 2022 to 2024 of 0.370 for electricity transmission and 0.400 for distribution, raising values below 0.4 by 0.02 (primary, p16). The November 2024 update (513/2024) kept the same values for 2025 to 2027, so the AI-era re-estimate left Italian electricity betas unchanged.
- **Germany, next period.** The comparator table is missing from the accessible version of the 2021 decision. The expert report for the fifth regulatory period of gas networks (Frontier Economics, Zechner and Randl, 13 July 2026, Table 3, p31) lists twelve comparators with 3- and 5-year asset betas; six of them (National Grid, Redeia, Terna, Snam, Enagás, Italgas) are also in Ofgem's RIIO-3 set. Values in `data/classification/bnetza_frontier_2026_comparator_betas.csv`; the estimation cut-off date is still to confirm.
- **Canada.** The OEB and AUC websites refuse automated requests, so the formula parameters remain from secondary sources. The formulas tie the return to bond yields and utility bond spreads with no beta term (secondary).

## Sources and what is known so far

### United States

- **FERC (interstate transmission).** Opinion 569 (November 2019) set the return from DCF and CAPM with equal weight; Opinion 569-A (2020) added a risk-premium model and was vacated by the D.C. Circuit; an October 2024 order for MISO transmission owners returned to DCF and CAPM. Proxy groups of comparable utilities supply the inputs. Source: [FERC news release, May 2020](https://ferc.gov/news-events/news/ferc-revises-public-utility-roe-methodology-sets-policy-natural-gas-oil-pipelines); [Opinion 569-A order](https://www.ferc.gov/sites/default/files/2020-06/E-1-052120.pdf); [S&P on the D.C. Circuit ruling](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2022/8/dc-circuit-ruling-gives-ferc-new-chance-to-establish-durable-transmission-roes-71694369).
- **New York (NYSPSC).** The commission's current method for the allowed return weights a CAPM estimate on a peer group of utilities at one third and a DCF estimate at two thirds (primary: Con Edison 10-K filed 15 February 2024, rate-making discussion; [filing](https://www.sec.gov/Archives/edgar/data/1047862/000104786224000012/ed-20231231.htm)). This is the only US state in the sample whose CAPM weight is stated in a filing so far.
- **State commissions (distribution and bundled service).** Each case is litigated with expert testimony using DCF, CAPM (often with Value Line betas, which are Blume-adjusted) and risk-premium models. Not yet verified from orders. Suggested sample: Virginia SCC (Dominion), Georgia PSC (Georgia Power), Texas PUC (Oncor, CenterPoint), Ohio PUCO (AEP Ohio), plus one low-exposure state. Recent context: median authorized electric return about 9.70% in the first nine months of 2025; SCE requested 11.75% and PG&E 11.30% for 2026 in California ([Edison 10-Q](https://www.sec.gov/Archives/edgar/data/827052/000082705225000100/eix-20250930.htm), [PG&E 10-Q](https://www.sec.gov/Archives/edgar/data/1004980/000100498025000148/pcg-20250930.htm)).

### United Kingdom (Ofgem)

- **RIIO-3 Final Determinations, December 2025** (electricity transmission, gas transmission and distribution, April 2026 to March 2031): [Finance Annex](https://www.ofgem.gov.uk/sites/default/files/2025-12/RIIO-3-Final-Determinations-Finance-Annex.pdf), allowed return on equity section from about page 44.
- Earlier stages: [Draft Determinations Finance Annex (July 2025)](https://www.ofgem.gov.uk/sites/default/files/2025-06/Draft-Determinations-Finance-Annex.pdf); [Sector Specific Methodology Decision Finance Annex (2024)](https://ofgem.gov.uk/sites/default/files/2024-07/RIIO-3_SSMD_Finance_Annex.pdf).
- Known so far: CAPM with betas from listed comparators; Ofgem signalled an asset beta in the upper half of 0.30 to 0.40; responses used a debt beta of 0.075 ([NERA response](https://www.spenergynetworks.co.uk/userfiles/file/Annex%202.1%20-%20250820_RIIO-3_cost_of_equity_response_DD_NERA_Final.pdf)); Oxera summary of the final determinations ([Oxera](https://www.oxera.com/insights/agenda/articles/riio-3-final-determinations/)).
- For H3: the betas behind RIIO-3 were estimated over windows that include 2023 to 2025, so any AI-era co-movement in National Grid and SSE could have entered the decision.

**Where each item sits in the Final Determinations Finance Annex** (176 pages; downloaded 7 November 2026). Chapter 3, "Allowed return on equity", runs from page 45 to 76. Page numbers are PDF pages from a keyword map.

| Item | Pages |
|---|---|
| Final allowed return and its components | p45 (chapter opening and summary) |
| Risk-free rate and whether it is indexed during the period | pp45 to 50; index-linked gilts mentioned on pp31, 45, 50 |
| Total market return or market risk premium | pp51 to 54 |
| Asset beta, debt beta, equity beta, re-levering | pp54 to 57 |
| Return frequency and estimation windows | p56, and pp54 to 58 generally |
| Notional gearing | pp45, 55, 59 |
| Comparators: which firms, and why | pp54 to 58; water companies (United Utilities, Severn Trent, Pennon) on pp63 to 68; National Grid on pp58, 63, 67 to 74; SSE on pp70 to 71 |
| Adjustments, cross-checks, outperformance | pp62 to 65, 70 to 71 |
| Final reasoning | pp72 to 76 |

**Implications for the design.**
1. Three of Ofgem's nine beta comparators are listed water companies (United Utilities, Severn Trent, Pennon; FD p58). A UK water placebo therefore overlaps with the regulator's own comparator set and is not an untreated control for the regulatory channel.
2. Only the risk-free rate is updated during 2026 to 2031; beta is fixed for five years once set (p45). An AI-era change in UK utility betas can reach allowed returns only at the next determination.

**Open questions.** Whether Ofgem adjusts for National Grid's large US business or down-weights it; whether the chosen asset beta moved from RIIO-2 to RIIO-3, and what Ofgem attributes any move to.

**AI in the annex.** The annex mentions AI once (p7), as a driver of electricity demand and network investment. A keyword search finds no mention in the cost-of-equity reasoning.

### Germany (BNetzA)

- **Fourth regulatory period:** equity return of 5.07% before corporate tax for new assets and 3.51% for old assets, set in 2021 ([BNetzA press release, October 2021](https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/DE/2021/20211020_EKZins.html?nn=265778)); a higher, variable rate for new investment set in January 2024 ([press release](https://bundesnetzagentur.de/SharedDocs/Pressemitteilungen/DE/2024/20240124_EKZins.html?nn=991502)).
- **Fifth period** (gas from 2028, electricity from 2029): method set on 8 December 2025; a single weighted average cost of capital; CAPM kept, with the market risk premium from historical excess returns ([BNetzA WACC FAQ](https://bundesnetzagentur.de/DE/Beschlusskammern/1_GZ/BK9-GZ/2026/2026_bis0999/BK9-29-0621/Downloads/FAQ_WACC.pdf); [Grant Thornton overview](https://www.grantthornton.de/themen/2025/aktuelle-entwicklungen-zur-eigenkapitalverzinsung-von-netzbetreibern-neue-wacc-berechnung-im-fokus/)).
- Comparators and windows: see the findings table (BK4-21-0055, pp25 to 37).

### Spain (CNMC)

- **Financial remuneration rate (TRF) 2026 to 2031:** 6.58%, approved December 2025 (proposed 6.46% in July 2025; 5.58% in 2020 to 2025), built on a WACC method ([CNMC press release](https://cnmc.es/prensa/circulares-retribucion-electrica-20250710?page=0); [Energías Renovables](https://www.energias-renovables.com/panorama/la-cnmc-fija-una-tasa-de-retribuci-20251223)). Reported as sent to the Consejo de Estado; check whether it is in force.
- Comparators and window: see the findings table (explanatory memo, pp75, 106).

### Italy (ARERA)

- **TIWACC 2022 to 2027:** delibera 614/2021/R/com ([Allegato A](https://www.ARERA.it/fileadmin/allegati/docs/21/614-21tiwacc.pdf)), amended by 654/2022, 139/2023, 196/2023 and 556/2023.
- **Mid-period update for 2025 to 2027,** including the asset beta: delibera 513/2024/R/com of 28 November 2024 ([text](https://arera.it/fileadmin/allegati/docs/24/513-2024-R-com.pdf)); tables 2 and 3 of the updated Allegato A hold the values.
- For H3: a beta update made in November 2024 is inside the AI era.

### Canada

- **Ontario (OEB):** generic cost of capital decision EB-2024-0063, 27 March 2025 ([decision page](https://oeb.ca/node/5097); [backgrounder](https://oeb.ca/sites/default/files/Cost%20of%20Capital-EB-2024-0063-BACKGROUNDER.pdf)); 2026 parameters from the same formulas ([OEB letter, October 2025](https://oeb.ca/sites/default/files/OEBLtr_2026%20CoC_20251031.pdf)). Historically a formula-based equity risk premium tied to bond yields; check the current formula.
- **Alberta (AUC):** Decision 27084-D02-2023 (October 2023) adopted a formula: equity risk premium on 30-year Government of Canada yields plus a utility bond spread, base 9.0%, recalculated each November ([AUC page](https://www.auc.ab.ca/cost-of-capital-parameters-in-2024-and-beyond/); [Bennett Jones summary](https://www.bennettjones.com/Insights/Updates/Alberta-Abandons-2004-ROE-Formula)).
- For H3: formula returns tied to bond yields, not betas, make Canada the natural "no pass-through" comparison, provided the formulas contain no beta term.
