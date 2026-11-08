# Results: H3 and H4

First estimates, 8 November 2026, under the frozen [pre-specification](prespecification.md) and the dated [implementation notes](analysis_notes.md). The H1 and H2 results are in [results_h1_h2.md](results_h1_h2.md).

## The AI era added a few basis points to regulatory betas, and none of it came from utilities' own AI exposure

For each determination, the regulator's beta was rebuilt from its own comparators, window, frequency and de-levering, and recomputed with AI-era returns put back on their pre-AI footing ([figure 4](../output/figures/fig4_h3_contribution_bps.png)):

| Determination | Replica check | AI-era contribution to the beta | Allowed return effect |
|---|---|---|---|
| UK, RIIO-3 (10 years of daily data to March 2025) | asset beta 0.370 against published 0.375; implied gearing 0.29 to 0.55 for all eight comparators | +0.006 asset beta | +6 bp at 55% gearing and a 4.6% premium |
| Spain, 2026 to 2031 (6 years of weekly data to December 2023) | levered betas correlate 0.99 with the CNMC's (mean gap 0.027); re-levered 0.78 against published 0.75 | +0.013 equity beta | +6 bp at the CNMC's 4.98% premium |
| Germany, prospective for the next electricity period (to October 2026) | 6 of 12 comparators pass the gearing check on 1 and 3 years, all 12 on 5 years | +0.024 to +0.038 asset beta | +22 to +35 bp at 40% equity and BNetzA's 3.7% premium |
| Italy, 2025 to 2027 | not replicated: comparator list not available | n/a | betas left unchanged by the November 2024 update |
| Canada | no beta in the formula | zero by construction | n/a |

**The channel.** Almost the whole contribution comes from the market index, not from the comparators: putting each firm's own AI loading back at its pre-AI value changes the beta by less than 0.002 everywhere. The index channel is mechanical. In the AI era, the local index moved less with semiconductor stocks per unit of their return (for the S&P 500, the slope fell from 0.47 to 0.34). Utilities move against the AI factor once the market is held fixed (H1), so a market that is less driven by chip stocks makes them look slightly riskier relative to it.

**Dose.** The size of the effect follows how much AI-era data the regulator's window contains: 2.3 of 10 years for Ofgem, 1 of 6 years for the CNMC, almost all of the window for a German estimate made in 2026. This matches design proposal P1.

**Cross-border.** For RIIO-3, 3.5 of the 6 basis points come from the four UK comparators and 2.5 from the four Spanish and Italian ones (design proposal P2).

## US rate cases: no significant pass-through in the pre-specified model, and the design cannot separate it from the post-2022 rise in allowed returns

For 85 US decisions, the holding company's beta was rebuilt at each order date like a Value Line beta (5 years of weekly data, two-thirds weight on the raw beta), but against the S&P 500 rather than Value Line's NYSE Composite. At the 32 decisions from 2023 on, the AI-era contribution averages +0.046 in adjusted-beta units (range 0.001 to 0.086), almost all through the index channel (−0.001 exposure, +0.045 composition).

Across 53 pairs of consecutive decisions in 18 states, the change in authorised ROE on the change in this contribution, controlling for the 10-year Treasury yield and the Baa spread:

| Specification | Coefficient (ROE points per unit of beta) | Standard error | Bootstrap p |
|---|---|---|---|
| State fixed effects (pre-specified) | 2.65 | 1.74 | 0.29 |
| No fixed effects | 2.51 | 0.76 | 0.047 |

The pre-specified estimate is not distinguishable from zero. Both estimates sit in the range H3 predicts (positive and below a 5 to 6 point premium), but neither can be read as pass-through of AI-driven beta: the contribution is zero for every decision before 2023 and positive after, so its change marks the first decision after 2022 and can absorb any post-2022 rise in allowed returns that the two interest-rate controls miss.

## H4: the money involved is small

- **UK.** +6 bp on RIIO-3 equity is about £0.27 million a year per £1 billion of regulatory asset value (45% equity). Company asset values were not collected.
- **US, latest AI-era decision per unit.** With the observed coefficient (not significant), the median is 15 bp, $7.3 million a year and $5.60 per customer a year (maximum $12). At a 6% premium with full CAPM weight, an upper bound, the median is 34 bp, $16 million a year and $12.60 per customer (maximum $27). Rate base is the stated figure for six units and the FERC net-plant proxy, which overstates by about 1.2 to 2.7 times, for the rest.
- **Spain and Germany.** Basis points only; regulated asset bases were not collected.

## Robustness

Five of the seven pre-specified checks apply to H3 (which ones, and why, was recorded before they ran). Basis points on the allowed return, "both" counterfactual (`output/tables/h3_robustness.csv`):

| Determination | Main | NVDA instead of SMH | USD-based | AI era from 2024 | National Grid half US |
|---|---|---|---|---|---|
| UK RIIO-3 | 6.1 | 1.9 | 5.4 | 4.5 | 8.4 |
| Spain 2026 to 2031 | 6.3 | 2.9 | 8.3 | 0 (window ends 2023) | n/a |
| Germany, prospective, 1 year | 30.1 | 10.2 | 32.1 | 32.1 | n/a |
| Germany, prospective, 3 years | 34.7 | 14.4 | 35.3 | 37.5 | n/a |
| Germany, prospective, 5 years | 22.1 | 8.9 | 19.0 | 21.6 | n/a |

The contribution is positive in every case except Spain under the 2024 start, where it is zero by construction. Its size depends on the AI factor: with NVDA in place of the semiconductor index it falls by half to two thirds, because the indices' co-movement with NVDA changed less than with SMH.

US panel, coefficient on the change in AI-era contribution (bootstrap p in brackets):

| Check | State fixed effects (pre-specified) | No fixed effects |
|---|---|---|
| Main | 2.65 (0.29) | 2.51 (0.05) |
| NVDA instead of SMH | 9.14 (0.31) | 8.61 (0.07) |
| AI era from 2024 | 1.94 (0.37) | 2.06 (0.10) |
| Excluding Edison and PG&E | 1.00 (0.74) | 1.87 (0.16) |

The pre-specified estimate is not significant in any check, and the no-fixed-effects estimate, borderline in the main run, is not significant in any check either. The NVDA coefficient is larger because the NVDA-based contribution is smaller (median 0.015 against 0.055), so the same ROE changes divide by a smaller number.

## What these results do not show

- They do not show that AI raised utilities' cost of capital through their own data-centre exposure: that channel is close to zero in every country.
- The index-channel effect is a property of how the market proxy relates to chip stocks; whether regulators should net it out is a policy question the estimates cannot settle.
- Italy is not replicated, Germany's replica rests on six comparators for the short windows, and the UK check uses gearing backed out from Ofgem's own asset betas rather than independent gearing data.

## Files

`output/tables/h3_uk_replica.csv`, `h3_uk_summary.csv`, `h3_de_replica.csv`, `h3_de_summary.csv`, `h3_es_replica.csv`, `h3_es_summary.csv`, `h3_us_decisions.csv`, `h3_us_panel.csv`, `h4_us.csv`. Code: `code/17_h3_replicas.py`, `code/18_h3_us_panel.py`, `code/16_figures.R`.

## Further checks (8 November 2026, written down before they ran)

Three checks were added after the first results ([analysis_notes.md](analysis_notes.md), last entries; `code/20_h3_further_checks.py`). Holding the semiconductor share of index variance, instead of the index's slope on semiconductor returns, at its pre-AI value roughly halves every contribution (UK 3.1, Spain 3.4, Germany 11.9 to 16.3 basis points) and sets the US contribution to about zero. Under the main counterfactual, month-block bootstrap intervals exclude zero, but placebo break dates in 2015 to 2021 give contributions at least as large in 87% of cases for the UK, 26% to 58% for the German windows and 5% of 585 usable breaks for Spain (`output/tables/h3_further_uncertainty.csv`, figure 5). In the US panel, the AI-era share of each decision's beta window explains 80% of the contribution across AI-era decisions, and with decision-year fixed effects the coefficient is −0.12 (standard error 2.32) (`output/tables/h3_further_us_timing.csv`).

Two reporting additions, recorded before they ran: with clustering by utility (22 utilities with consecutive decisions), as the pre-specification named, the pre-specified US coefficient has a standard error of 1.51 (bootstrap p = 0.08), against 1.74 (p = 0.29) with clustering by state (`output/tables/h3_further_us_clustering.csv`). Ending Ofgem's 10-year window on 31 December 2024 or 30 September 2025 instead of 31 March 2025 gives a UK contribution of 5.4 or 9.3 basis points (`output/tables/h3_further_uk_end_dates.csv`).
