# Does the AI Boom Raise Utilities' Cost of Capital? Evidence across Regulatory Regimes

**Status (7 November 2026):** design decided (D1 to D5); pre-specification ([prespecification.md](prespecification.md)) and exposure rule ([exposure_rule.md](exposure_rule.md)) frozen the same day. Price data downloaded and coverage checked (`output/tables/data_coverage.csv`); no returns analysed.

---

## 1. Question

Regulators set the return on equity that regulated electricity networks are allowed to earn, and customers pay it through their bills. In many regimes the allowed return rests partly on the capital asset pricing model (CAPM), which uses each utility's measured market risk, its beta. If the AI investment boom has made utility shares move more with technology stocks, measured betas rise, allowed returns rise at the next review, and households pay more, even where no data centre connects.

The project asks two linked questions:
1. Has utilities' co-movement with AI assets, and their measured beta, risen since the AI boom began, and is the rise concentrated in utilities exposed to data-centre demand?
2. Where regulators feed current market betas into allowed returns, has any rise reached allowed returns, and what is it worth in money?

## 2. Stakes for consumers and regulators

- The allowed return is one of the largest single parameters in a network bill. Dunkle Werner and Jarvis (Energy Institute at Haas WP 329R) estimate that US allowed returns above the cost of capital cost consumers about $7 billion a year, and Rode and Fischbeck (2019) document a rising premium of allowed returns over benchmarks.
- A financial channel from AI to bills would reach households who never see a data centre, and would be invisible in studies of physical load and wholesale prices.
- Regulators and consumer advocates can act on it: by choosing beta estimation windows and comparator sets, or by excluding AI-driven co-movement as non-diversifiable risk that the network does not bear.

## 3. Mechanism and hypotheses (revised 7 November 2026; proposals P1 to P5 adopted)

Regulators estimate the cost of equity as r_e = r_f + β_e · MRP (plus adjustments), with β_e taken from listed comparators, measured against a local market index over a fixed window.

**Two channels with opposite signs.** A utility's beta against its local index is β = cov(u, m) / var(m). Split the index return into the part explained by the AI factor and the rest, m = m_AI + m_other. Then

β = [cov(u, m_AI) + cov(u, m_other)] / var(m).

- **Exposure channel (numerator):** utilities exposed to data-centre demand co-move more with AI stocks, so cov(u, m_AI) rises and beta rises.
- **Composition channel (denominator):** where AI stocks dominate the index, var(m) rises with AI volatility. A utility that does not move with AI stocks then shows a lower beta, and so a lower allowed return.

The net sign is the question. The identity makes the split exact: each utility's change in beta between two windows decomposes into a numerator-AI term, a numerator-other term and a denominator term.

| | Hypothesis | Test |
|---|---|---|
| H1 | Utilities' co-movement with AI stocks changed after 30 November 2022, more for utilities exposed to data-centre demand. | Rolling betas on market, AI and rate factors; Diebold and Yilmaz spillover index; dynamic correlations |
| H2 | The net change in regulator-style betas depends on the balance of the two channels. It is more positive where utilities are exposed to data-centre demand, and more negative where the local index's variance is dominated by AI stocks. | Exact beta decomposition, utility by utility, in each regulator's window and frequency; cross-country comparison by the index's AI share of variance |
| H3 | Allowed returns move with the AI-era component of the beta each determination actually used, in proportion to how much AI-era data that determination could absorb, including through foreign comparators. | Counterfactual replica of each determination (below); comparator map across borders |
| H4 | The AI-era component is worth a measurable amount on bills. | Basis points of allowed return times equity in the regulated asset base, per determination and per customer |

## 4. Cross-country design

**Exposure to AI-era betas, per determination (P1).** Replicate each regulator's beta calculation with its own comparators, window, frequency, index and adjustment, using actual returns. Then replicate it again with AI-era co-movement removed: on dates after 30 November 2022, each comparator's return has its AI-factor component replaced by the component implied by its pre-AI loading. The difference between the two replicas, times the regulator's market risk premium, is the AI-era contribution to that determination's allowed return in basis points. This replaces the earlier 2 × 2 with one continuous number per determination:
- It is zero by construction in Canada, where returns follow a bond-yield formula.
- It is near zero where the window ends before 2023 (most of Italy's 2019 to 2023 window).
- It is largest where windows are short and recent (Germany from 2029, US rate cases).

**Comparators across borders (P2).** For each determination, record each comparator's country. The AI-era contribution then splits into domestic and foreign parts. For example, part of the UK's RIIO-3 beta comes from Spanish and Italian networks.

**Index composition as moderator (P3).** For each country and window, compute the share of local index variance explained by the AI factor (rolling R²). The composition channel predicts larger negative beta effects where that share is high (the S&P 500) than where it is low (FTSE, IBEX, FTSE MIB, TSX).

**Placebos (P4).** US water and gas utilities, and UK water companies for H1 and H2 only. UK water companies are Ofgem comparators, so they are part of H3's treatment, not a placebo for it.

**Germany (P5).** H1 and H2 only. Its next electricity determination applies from 2029, which will be an out-of-sample test of H3.

If co-movement and betas changed alike for exposed utilities, unexposed utilities and placebos, a global factor such as interest rates is the driver, not AI.

**Countries (decision D1, decided).** Regulatory methods are now extracted from primary documents in [`regulator_methods.md`](regulator_methods.md). The table below is the original screening.

| Country | Regulator and method (to verify) | Listed regulated firms in the data | Data-centre exposure |
|---|---|---|---|
| United States | State commissions; litigated rate cases; CAPM, DCF and risk-premium evidence with current market betas | 33 electric utilities; water and gas placebos | High (Northern Virginia, Texas, Arizona, Ohio) |
| United Kingdom | Ofgem RIIO price controls every five years; CAPM with betas from listed comparators (RIIO-3 asset beta about 0.30 to 0.40 in an Oxera report for National Grid) | National Grid, SSE; three listed water companies as placebos | Moderate (London and Slough) |
| Germany | BNetzA sets the equity return per regulatory period, CAPM-based, with a convenience-yield uplift in the fourth period | E.ON (RWE as a merchant benchmark) | Moderate (Frankfurt) |
| Spain | CNMC financial remuneration rate per regulatory period | Redeia, Enagás; Iberdrola and Endesa mixed | Growing (Madrid) |
| Italy | ARERA WACC methodology with periodic updates | Terna, Snam, Italgas; Enel, Acea mixed | Growing (Milan) |
| Canada | Provincial regulators; Ontario uses a formula return tied to bond yields | Hydro One, Fortis, Emera, Canadian Utilities | Moderate (Quebec, Ontario) |
| Australia | AER Rate of Return Instrument with a fixed equity beta and gearing | Few listed regulated networks remain (APA partly regulated) | Moderate (Sydney, Melbourne) |
| Japan | Cost-based tariff regulation | TEPCO, Kansai Electric | Growing (Tokyo, Osaka) |

Ireland and the Netherlands have very high data-centre shares but no listed regulated networks, so they cannot enter the equity analysis.

## 5. Data

| Item | Source | Status |
|---|---|---|
| Daily adjusted prices, 2012 to November 2026, 80 series (utilities, market indices, SMH, NVDA, FX) | Yahoo Finance | Downloaded 7 Nov 2026; coverage complete except later listings (Hydro One 2015, Italgas 2016, Vistra 2016, Constellation 2022) |
| Interest rates (10-year government yields) | FRED (US), Bank of England, Bundesbank, Banco de España, Bank of Canada; ECB euro-area series as the candidate for Italy | Downloaded 7 Nov 2026 (`output/tables/yields_coverage.csv`). No official daily Italian series found; ECB euro-area series used for Italy, Bund as robustness (pre-specification, Amendment 1) |
| Allowed returns on equity by determination | US: commission orders (the standard compilation, S&P Global RRA, is proprietary); UK: Ofgem final determinations; Germany: BNetzA; Spain: CNMC; Italy: ARERA; Ontario: OEB; Australia: AER | To do (decision D5) |
| Data-centre exposure per utility | US: main 10-K text (FY2023, FY2024). Outside the US: hub flags (`data/classification/hub_flags_nonus.csv`) | US collected; non-US hub flags coded 7 Nov 2026. The IEA publishes no country-level data-centre share for the five non-US countries, so the hub flag is the non-US measure (pre-specification, Amendment 2) |

## 6. Method (fixed in [prespecification.md](prespecification.md))

1. **Returns.** Daily and weekly log returns in local currency.
2. **AI factor.** SMH return orthogonalised to the local market return, as in the DeepSeek study; NVDA as an alternative. Currency treatment is decision D3.
3. **Interest-rate factor.** Change in the local 10-year government yield, included in every factor model. Utilities trade partly as bond substitutes, and the 2022 rate rise is the main competing explanation for any change in their risk.
4. **H1.** Rolling 2-year three-factor betas (market, AI, rates) by utility; Diebold and Yilmaz (2012) generalised-VAR spillover index between country utility portfolios, the AI factor and rates; dynamic conditional correlations. Before and after 30 November 2022, by exposure.
5. **H2.** Replica betas: each regulator's window, frequency, comparator set and adjustment (for example the Blume adjustment used in US testimony). Difference-in-differences: exposed versus unexposed utilities, before versus after, with water utilities as placebos.
6. **H3.** Allowed returns at successive determinations regressed on the change in replica beta, interacted with regime type.
7. **H4.** Basis points times equity in rate base, per utility and per customer where customer counts are available.

Inference: utility-clustered standard errors and wild cluster bootstrap where clusters are few; placebo dates for the before/after splits.

## 7. Threats

| Threat | Response |
|---|---|
| Interest rates, not AI, changed utilities' risk after 2022 | Rate factor in every model; placebo water and gas utilities, which share rate exposure but not AI exposure |
| Europe's 2022 energy crisis changed European utility risk at the same time | Analyse Europe from 2023; mixed generators separated from networks |
| Firm-specific shocks (California wildfire liabilities, takeovers) | Flag and drop in robustness (EIX, PCG) |
| National Grid and Fortis own large US networks | Treat by asset location in robustness |
| Few listed regulated firms outside the US | Country portfolios; inference that respects few clusters; the US carries within-country power |
| AI factor in USD, utilities in local currency | Decision D3; FX-adjusted and local-currency versions reported |

## 8. Design decisions

| | Decision | Options | Notes |
|---|---|---|---|
| D1 | Countries | **Decided 7 November 2026: core six, US, UK, Germany, Spain, Italy, Canada.** Australia and Japan stay in the price data for descriptive comparison only and enter no hypothesis test. | Australia has almost no listed regulated networks left; Japan's cost-based tariffs do not use market betas in the same way |
| D2 | How each regulator estimates beta and the return on equity | **Done 7 Nov 2026.** Extracted from the latest determination for each D1 country: window, frequency, comparators, adjustments ([`regulator_methods.md`](regulator_methods.md)) | The step referees will test hardest |
| D3 | AI factor currency | **Decided 7 Nov 2026.** everything in local currency. Utility and index returns as regulators measure them; SMH converted to local currency at daily FX, then orthogonalised to the local index. USD-based version as robustness | Regulators measure betas in local currency against local indices (Ofgem p56; ARERA p4), so the replicas must too |
| D4 | Data-centre exposure measure | **Decided 7 Nov 2026; revised after collection:** 10-K text intensity, FY2023 primary, FY2024 in ranks as robustness (coding rule in [exposure_rule.md](exposure_rule.md)). Original draft: US firm-level, from each utility's announced data-centre or large-load pipeline in investor materials for Q4 2024 (MW of signed or advanced requests, scaled by peak load); outside the US, each utility's share of assets in a data-centre hub region. Coding rule frozen 7 November 2026 | Firm-level variation exists mainly in the US; elsewhere there are too few listed utilities for firm-level measures to add much |
| D5 | US allowed returns source | **Decided 7 Nov 2026, revised the same day:** all 33 US holding companies, one rate unit each (the utility-state pair with the largest 2023 deliveries), every base-rate order from 2015 to 2026; rule in [ratecase_rule.md](ratecase_rule.md), frozen 7 Nov 2026 before collection. S&P Global RRA access would be an upgrade | RRA would cover every case but is proprietary |

## 8b. What the regulators' documents changed (7 November 2026; all five proposals adopted the same day and written into sections 3 and 4)

Details and page citations: [`regulator_methods.md`](regulator_methods.md).

**P1. How much AI-era data each regulator's beta can absorb.** How much AI-era data (2023 onward) a regulator's beta can absorb depends on its window and selection rule: roughly 10% to 30% of a 10-year window filtered through a wide range in the UK, about half of a 6-year window in Spain, at most one year of a 5-year window in Italy (2019 to 2023), heavy weight on the latest year in Germany but not applied until 2029, current in US rate cases, and zero in Canada's bond-yield formula. Proposal: replace the binary regime split in the 2 × 2 with a continuous "regulatory exposure to AI-era betas" for each determination.

**P2. Comparator sets carry betas across borders.** Ofgem's comparators include Spanish and Italian networks (Enagás, Snam, Redeia, Terna, Italgas); BNetzA uses foreign network operators; CNMC uses 34 European comparators. An AI-driven change in one country's utility betas can therefore move allowed returns in another country. Proposal: map each determination's comparators and test this channel directly.

**P3. Two channels with opposite signs.** Betas are measured against a local index.
- Exposure channel: utilities exposed to data-centre demand co-move more with AI stocks, so beta rises.
- Composition channel: where the index itself is dominated by AI stocks (the S&P 500 far more than the FTSE, IBEX or FTSE MIB), the market's swings are increasingly AI swings. Utilities that do not move with AI stocks then show a lower beta, so allowed returns and bills fall.
In the DeepSeek study, regulated US utilities loaded negatively on the orthogonalised AI factor during 2024 (mean about −0.41), which fits the composition channel. Proposal: make the net sign the question, with the index's AI weight as a cross-country moderator.

**P4. UK placebo overlap.** Ofgem uses the three listed water companies as beta comparators, so they cannot serve as a clean UK placebo for H3 (they remain valid for H1 and H2). Their 2-year betas in the draft determinations (0.38 to 0.46) were above their 10-year betas (0.32 to 0.39), a rise that AI cannot explain.

**P5. Germany cannot test H3 yet.** Its next electricity determination applies from 2029. Germany stays in H1 and H2 and becomes an out-of-sample H3 test later.

## 9. Literature (to be expanded)

| Reference | Role | Verified |
|---|---|---|
| Rode, D. C., & Fischbeck, P. S. (2019). Regulated equity returns: A puzzle. *Energy Policy*, 133, 110891. | Allowed-return premium over benchmarks has risen for decades | Yes |
| Dunkle Werner, K., & Jarvis, S. Rate of Return Regulation Revisited. Energy Institute at Haas WP 329R (revised 2025). | Allowed returns adjust asymmetrically; excess cost about $7 billion a year to US consumers | Yes (figures differ across versions) |
| Diebold, F. X., & Yilmaz, K. (2012). Better to give than to receive: Predictive directional measurement of volatility spillovers. *International Journal of Forecasting*, 28(1), 57 to 66. | Spillover index | Yes |
| Van Nieuwerburgh, S. (2026). Financing the AI Buildout. *Brookings Papers on Economic Activity* conference draft. | Rolling betas of data-centre REITs; nothing on utilities or rate cases | Yes (text read) |
| Blume, M. E. (1971). On the assessment of risk. *Journal of Finance*, 26(1). | Beta adjustment used in rate-case testimony | Not yet |

**Novelty check (7 November 2026).** Web and Scholar searches found no study linking AI exposure to utilities' measured beta or allowed returns.
