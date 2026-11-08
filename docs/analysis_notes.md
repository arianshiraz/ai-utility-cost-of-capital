# Implementation notes for the frozen tests

Written 8 November 2026, before any utility returns were analysed. These notes settle details that [prespecification.md](prespecification.md) leaves open. They do not change any test. Later changes are added as dated entries.

## Returns and factors

- **Returns.** Daily log returns of adjusted closing prices on each market's own trading days. A day enters a regression only if the utility, the local index, SMH and the yield series all have a value. Weekly returns run from Friday close to Friday close, as specified.
- **AI factor.** SMH is converted to local currency each day (SMH in dollars divided by the dollar price of one unit of local currency), and its log return is regressed on the local index return within each estimation window. The residual is the orthogonalised AI factor. NVDA is treated the same way for robustness check 1.
- **Asynchronous closes.** European and Canadian markets close before SMH's US close, so a day's AI news can appear in the next day's European return. Daily estimates for non-US firms are therefore biased towards zero; the weekly results (robustness check 5) are the check on this.
- **Rate factor.** Daily change in the 10-year yield in percentage points. Italy uses the ECB euro-area series (Amendment 1).

## H1

- **Sample.** The 42 regulated electric utilities: 33 US and 9 outside the US. Water and gas utilities are placebos; mixed firms and merchant generators are not used in the tests.
- **Exposure scales differ.** US exposure is continuous (FY2023 data-centre mentions per 10,000 words); outside the US it is the hub flag. A single regression with country fixed effects would identify the slope almost entirely from US firms, because within-country variation outside the US comes from two countries only (UK: SSE versus National Grid; Canada: Hydro One versus three others). So:
  - main test: the US cross-section, change in AI beta on exposure, heteroskedasticity-robust (HC1) standard errors;
  - secondary: all 42 firms with exposure standardised within each country and country fixed effects, wild cluster bootstrap by country (Webb six-point weights, 9,999 draws), reported with the warning that six clusters is few.
- **US placebo.** FY2023 data-centre mentions are measured for the five US water and gas utilities with the same 10-K method. The placebo test is the same regression on those five firms, and a pooled test of whether the electric slope differs from the placebo slope.
- **Placebo breaks.** 1,000 break dates drawn uniformly from 1 January 2015 to 31 December 2021 (seed 20261108). For each, the pre and post windows have the same lengths as the main windows and the COVID exclusion applies where it falls inside them. Pre windows are cut at 2 January 2012, where the price data start, and post windows are cut at 29 November 2022, so that no placebo window reaches into the AI era. The reported p-value is the share of placebo slopes at least as large as the AI-era slope (one-sided, as H1 predicts a positive slope), with the two-sided share alongside.
- **Takeover exclusion.** No sample firm was the target of a takeover completed in the sample. Evergy was formed by a merger completed on 4 June 2018 and its shares start trading then, so its pre-AI window starts on 4 June 2019, twelve months after completion. Texas-New Mexico Power's parent TXNM Energy agreed in 2025 to be acquired; if that acquisition completes before 31 October 2026, TXNM is dropped from the AI-era window from twelve months before completion.

## H2

- **Windows.** Each country's regulator window and frequency from the pre-specification, ending 29 November 2022 and 31 October 2026. Where a regulator uses several windows, all are reported and the one the regulator weights most is marked as main: UK 10 years, Germany 1 year.
- **Decomposition.** For each utility and window: C = cov(u, m), m_AI is the fitted value from regressing the local index return m on the raw (not orthogonalised) local-currency SMH return, C_ai = cov(u, m_AI), C_o = cov(u, m − m_AI), V = var(m). The change in beta between the two windows is split exactly into ΔC_ai/V_b, ΔC_o/V_b and C_a(1/V_b − 1/V_a), where a is the earlier window and b the later one. The three terms sum to the change in beta by construction; the script checks this.
- **Index AI share.** R² of the local index on the raw SMH return in each window.
- **Tests.** (1) The exposure term on exposure, with the same two specifications as H1. (2) Across the six countries, the composition term (country mean over regulated electric utilities) against the change in the index AI share. With six points this is reported as a correlation and a slope, without a formal test. (3) Net change in beta by country, sign reported.

## Dated entries

**8 November 2026, before H1 was run: US placebo exposure is zero for every placebo firm.** The five US water and gas utilities (AWK, WTRG, ATO, OGS, SR) have no data-centre mentions in their FY2023 10-Ks (`output/tables/dc_exposure_placebo.csv`; Atmos and Spire use September fiscal years, so their FY2023 10-Ks are those filed in late 2023). The pre-specified placebo slope cannot be estimated without variation in exposure. The placebo test is therefore the coefficient on a placebo indicator in a pooled regression of the change in AI beta on exposure (electric firms) and the placebo indicator: a placebo coefficient near zero means water and gas utilities moved like electric utilities with no data-centre exposure, which is what H1 expects if the AI channel runs through exposure.
