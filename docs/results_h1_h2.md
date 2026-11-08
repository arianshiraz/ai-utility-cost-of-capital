# Results: H1 and H2

First estimates, 8 November 2026, under the frozen [pre-specification](prespecification.md) and the [implementation notes](analysis_notes.md). H3 and H4 are not yet estimated.

## H1: utilities with more data-centre exposure did not become more correlated with AI stocks

Across the 33 US regulated electric utilities, the change in the AI-factor loading between the pre-AI period (2017 to November 2022, COVID months excluded) and the AI era (2023 to October 2026) is unrelated to FY2023 data-centre exposure. The slope is −0.003 per data-centre mention per 10,000 words (standard error 0.028). For scale, the most exposed utility in FY2023 had 0.98 mentions per 10,000 words, so the fitted difference between it and a utility with none is about −0.003, against a cross-utility standard deviation of the change of about 0.06 ([figure 1](../output/figures/fig1_h1_exposure_scatter.png)).

- **Placebo break dates.** In 70% of 1,000 placebo splits between 2015 and 2021 the slope is at least as large as in the AI era ([figure 2](../output/figures/fig2_h1_placebo_breaks.png)). Neighbouring break dates share most of their windows, so this is a rank among a few distinct pre-AI periods, not 1,000 independent draws.
- **Water and gas placebo.** US water and gas utilities, none of which mention data centres, moved like electric utilities with no exposure: the placebo indicator is −0.016 (0.036).
- **All countries.** With exposure standardised within each country and country fixed effects, the slope is −0.0015, wild-cluster-bootstrap p = 0.28 across six country clusters.
- **Robustness.** None of the six checks that apply to H1 changes the answer: NVDA instead of SMH (−0.010, SE 0.018), dropping Edison International and PG&E (−0.015, 0.025), starting the AI era in January 2024 (−0.022, 0.036), weekly returns (0.028, 0.036), FY2024 exposure in ranks (0.001, 0.001), and the FY2023 any-mention indicator (−0.002, 0.018).

The levels are more telling than the changes. US regulated utilities load negatively on the AI factor once the market is held fixed, about −0.27 in both periods, as in the [DeepSeek study](https://github.com/arianshiraz/deepseek-power-event-study). Merchant generators (Vistra, Constellation) moved from −0.32 to +0.46. This pattern is consistent with investors pricing AI demand into generators that sell at market prices rather than into regulated networks, and it held even for the regulated utilities that disclose the most data-centre activity.

**What this does not show.** The exposure measure counts mentions in one annual report; it may miss load that utilities discuss elsewhere. Thirty-three utilities give little power to detect a small slope: the 95% confidence interval runs from about −0.06 to +0.05.

## H2: regulator-style betas fell, and the fall is not concentrated in exposed utilities

In each country's regulator window, the average beta of regulated electric utilities fell between the window ending November 2022 and the window ending October 2026 ([figure 3](../output/figures/fig3_h2_decomposition.png)):

| Country | Window | Utilities | Beta, 2022 window | Beta, 2026 window | Change |
|---|---|---|---|---|---|
| US | 5 years, weekly | 33 | 0.82 | 0.36 | −0.46 |
| UK | 10 years, daily | 2 | 0.76 | 0.76 | −0.01 |
| Germany | 1 year, daily | 1 | 0.71 | 0.40 | −0.31 |
| Spain | 6 years, weekly | 1 | 0.50 | 0.33 | −0.17 |
| Italy | 5 years, daily | 1 | 0.63 | 0.35 | −0.27 |
| Canada | 5 years, weekly (descriptive) | 4 | 0.60 | 0.35 | −0.26 |

- **Test 1, exposure term on exposure.** No relation: US slope 0.04 (standard error 0.10); all countries, bootstrap p = 0.35.
- **Test 2, composition.** Across the six countries, the correlation between the composition term and the change in the index's AI share is −0.20. The index's AI share, measured as the R² of the index on the semiconductor index, fell in every country, so the premise of this test did not hold in the data.
- **Test 3, net change.** Negative in five countries and close to zero in the UK.

**What the decomposition can and cannot say.** The three terms add up exactly to the change in beta. The term labelled composition, however, mostly reflects lower market volatility: every earlier window contains the 2020 crash, so market variance fell and the term is positive everywhere. It is reported as index variance. The exposure and non-AI terms are both negative in every country, so utilities co-moved less with both the AI-linked and the other parts of the index.

A regulator that re-estimated beta in 2026 on its usual window would find a lower beta than in 2022 in every country studied except the UK, where the 10-year window barely moved. If anything, current market evidence points to lower, not higher, allowed returns from the CAPM component. Whether actual decisions followed is H3.

## Files

Estimates: `output/tables/h1_utility_betas.csv`, `h1_tests.csv`, `h1_placebo_breaks.csv`, `h2_decomposition.csv`, `h2_country.csv`, `h2_tests.csv`. Code: `code/12_returns.py` to `code/16_figures.R`.
