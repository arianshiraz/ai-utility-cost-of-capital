# Pre-specification of tests

**Status:** frozen on 7 November 2026, before any utility returns were analysed (only data coverage had been checked). Any later change is logged as a dated amendment with its reason, and results are reported under both the original and the amended specification.

## 1. Common definitions

| Item | Specification |
|---|---|
| Sample | Daily prices, 2 January 2012 to 6 November 2026 |
| AI era | From 30 November 2022 (public release of ChatGPT) |
| Pre-AI comparison period | 1 January 2017 to 29 November 2022, excluding 24 February to 30 June 2020 (COVID crash) |
| AI-era period | 1 January 2023 to 31 October 2026 |
| Returns | Log returns in local currency. Weekly returns are Friday close to Friday close. |
| Market index | The local index each regulator uses, or its closest available equivalent: S&P 500 (US); FTSE All-Share if available, otherwise FTSE 100 (UK); CDAX if available, otherwise DAX (Germany); IBEX 35 (Spain); FTSE MIB (Italy); S&P/TSX Composite (Canada). Any substitution is recorded. |
| AI factor | SMH total return converted to local currency at daily FX, orthogonalised to the local index within each estimation window. NVDA is the alternative factor. |
| Rate factor | Daily change in the national 10-year government bond yield (US: FRED DGS10; UK: Bank of England; Germany: Bundesbank; Spain and Italy: national central bank or ECB series; Canada: Bank of Canada). If a daily series is unavailable, the rate factor enters at weekly frequency. |
| Utility groups | Regulated electric (H1 to H4); water and gas placebos; merchant benchmarks (descriptive only); mixed firms (robustness only) |
| Exclusions | EIX and PCG in robustness (wildfire liabilities); any utility in the 12 months around a completed takeover |
| Exposure | As fixed in [`exposure_rule.md`](exposure_rule.md): primary FY2023 data-centre mentions per 10,000 words of the main 10-K; secondary FY2023 any-mention indicator; FY2024 in ranks as robustness. Outside the US: the country-level data-centre share of demand with the hub indicator. |

## 2. H1: co-movement with AI stocks

**Model.** For each utility, r_u = a + b_m · m + b_ai · ai⊥ + b_r · Δy + e, estimated on daily returns separately in the pre-AI and AI-era periods.

**Outcome.** Change in b_ai (AI era minus pre-AI), and change in the partial R² of the AI factor.

**Test.** Cross-sectional regression of the change in b_ai on data-centre exposure, with country fixed effects, for regulated electric utilities. H1 predicts a positive slope. Placebo: the same regression for water and gas utilities, where no slope is expected.

**Descriptive companion.** Diebold and Yilmaz (2012) spillover index from a VAR on weekly returns of country utility portfolios, the AI factor and the rate factor; 104-week rolling windows, 10-week generalised forecast-error variance decomposition. Reported as figures, not as a formal test.

## 3. H2: decomposition of regulator-style betas

**Windows.** Each country's regulator window and frequency, ending (a) 29 November 2022 and (b) 31 October 2026:
- US: 5 years, weekly;
- UK: 10, 5 and 2 years, daily;
- Germany: 1, 3 and 5 years, daily;
- Spain: 6 years, weekly;
- Italy: 5 years, daily;
- Canada: 5 years, weekly (descriptive, since no beta enters its formula).

**Decomposition (exact).** With C = cov(u, m) split into C_ai = cov(u, m_AI) and C_o = cov(u, m_other), where m_AI is the fitted value from regressing m on the raw AI factor, and V = var(m):

Δβ = (ΔC_ai) / V_b + (ΔC_o) / V_b + C_a · (1/V_b − 1/V_a)

The three terms are the exposure channel, the non-AI channel and the composition channel.

**Index AI share.** R² of the local index on the raw AI factor in each window.

**Tests.**
1. Exposure-channel term regressed on data-centre exposure (country fixed effects): positive slope predicted.
2. Composition term against the change in the index AI share across countries: negative relationship predicted.
3. Net Δβ by country: sign reported, with no direction predicted.

## 4. H3 and H4: counterfactual replicas of each determination

**Determinations in scope.** UK RIIO-3 Final Determinations (December 2025); Spain's financial remuneration rate for 2026 to 2031 (December 2025); Italy's 2025 to 2027 beta update (November 2024); US rate-case decisions collected under D5; Canada (zero by construction, verified by checking that the formula contains no beta); Germany as a prospective calculation for the 2029 period.

**Replica.** Reproduce each regulator's beta with its own comparators, window, frequency, index, adjustment (Blume or Vasicek) and de-levering. The replica is checked against the published value; any gap above 0.05 in asset beta is reported and explained before counterfactuals are computed.

**Counterfactuals.** On AI-era dates:
- (i) exposure counterfactual: each comparator's return has its AI-factor loading reset to its pre-AI value;
- (ii) composition counterfactual: the index return has its AI-factor loading reset to its pre-AI value;
- (iii) both.

**Outcome.** Basis points of allowed return = (replica beta − counterfactual beta) × the regulator's market risk premium, re-levered at the regulator's notional gearing. Split into domestic and foreign comparators (P2).

**Money (H4).** Basis points × equity share of the regulated asset base for each determination, per year; per customer where customer numbers are published.

**US panel test.** For each US decision, the change in authorised return on equity regressed on the counterfactual AI-era contribution computed at the decision date, controlling for the change in the 10-year Treasury yield and in utility bond spreads, with state fixed effects. H3 predicts a positive coefficient, below the full market risk premium, because commissions weight CAPM only partly.

## 5. Inference

- Utility-clustered standard errors. Wild cluster bootstrap by country where countries are the clusters.
- **Placebo breaks.** 1,000 random break dates between 1 January 2015 and 31 December 2021, each with the same pre and post lengths as the main split. The AI-era estimate is compared with the distribution of placebo-break estimates, as with the placebo dates in the DeepSeek study.

## 6. Robustness (fixed list)

1. NVDA instead of SMH.
2. A USD-based version (D3 alternative).
3. Excluding EIX and PCG.
4. AI era starting 1 January 2024 (after the 2023 rate peak).
5. Weekly instead of daily returns for H1.
6. Exposure measured by the FY2024 vintage in ranks, and by the FY2023 any-mention indicator.
7. National Grid treated as half US, half UK.

## 7. What would count against the hypotheses

- H1: no relation between exposure and the change in AI co-movement, or the same relation among placebos.
- H2: an exposure term no different from zero, and a composition term that does not vary with the index's AI share.
- H3: allowed returns that do not move with the replica's AI-era contribution in the US panel, or replica contributions that are economically trivial everywhere.

These outcomes would be reported as results, not as failures.
