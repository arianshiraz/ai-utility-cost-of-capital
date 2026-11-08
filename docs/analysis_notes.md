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

**8 November 2026, written after the H1 and H2 results were seen.** Two points about reading the results, not changes to any test.
1. *The H2 "composition" term mostly measures the change in market variance.* The term is C_a(1/V_b − 1/V_a). The earlier window of every country contains the 2020 COVID crash, so V_a is larger than V_b and the term is positive in every country. It therefore moves with the end of COVID-era volatility rather than with AI firms entering the index. The decomposition is exact, but the label overstates what the term isolates; it is reported as "index variance (labelled composition)".
2. *The placebo-break p-value is coarse.* Break dates a few weeks apart share most of their estimation windows, so the 1,000 placebo slopes are strongly dependent and form a few clusters (`output/figures/fig2_h1_placebo_breaks.png`). The p-value should be read as the AI-era slope's rank among a small number of effectively distinct pre-AI periods.

## H3 and H4 (written 8 November 2026, before any H3 or H4 estimate)

**Counterfactual returns.** On every AI-era date (from 30 November 2022):
- exposure counterfactual: r_cf = r − (b_ai,AI − b_ai,pre) · ai_perp, where the two loadings are the firm's three-factor AI loadings in the H1 pre-AI and AI-era windows (same frequency as the replica);
- composition counterfactual: m_cf = m − (g_AI − g_pre) · smh, where g is the slope of the local index on the raw local-currency SMH return in the same two windows;
- both: the two together. Before 30 November 2022 the counterfactual series equal the actual ones.

**UK (RIIO-3).** Ofgem estimates daily OLS equity betas against the most diversified local index and de-levers with Harris-Pringle (asset beta = (1 − g) equity beta + g × 0.075), with main weight on 10-year betas (Draft Determinations Finance Annex pp55 to 56). The annex does not publish each comparator's gearing or the data cut-off date.
- Window: 10 years ending 31 March 2025, the date of the risk-free rate Ofgem used in the Draft Determinations (p59). Indices: FTSE All-Share (UK), IBEX 35 (Spain), FTSE MIB (Italy); the broadest indices available in the data.
- Gearing: each comparator's gearing is backed out from Ofgem's own 10-year asset beta (Table 16) and the replica equity beta, and held fixed in the counterfactual (AI news does not change gearing). The replica check is therefore not the asset beta itself but whether the implied gearing is plausible for the company (between 0.2 and 0.75); a comparator outside that range is reported and its contribution shown separately.
- Replica asset beta: mean over the eight comparators with 10-year betas. It is compared with the published 0.375.
- Basis points: change in asset beta, re-levered at 55% notional gearing (electricity transmission), times the market risk premium of 4.6% (total market return 6.9% minus risk-free rate 2.3%, CPIH-real, Final Determinations p45). Domestic (four UK comparators) and foreign (four European) contributions are reported separately.

**Germany (prospective, next electricity period).** The 2021 comparator table is missing, so the prospective calculation uses the twelve comparators of the July 2026 expert report and its STOXX Europe 600 or national-index columns, on 1, 3 and 5-year daily windows ending 31 October 2026, with the Vasicek adjustment omitted and no tax term in de-levering, because the report's adjustment inputs are not reproduced. The replica is compared with the report's 3 and 5-year asset betas.

**Spain.** The CNMC used six years of weekly data to 31 December 2023 on 34 comparators (memo p75, Cuadro 26). If the comparator list can be mapped to price series, the same counterfactual is applied; otherwise the AI-era share of the window (one year of six) is reported as an upper bound on exposure and the replica is marked not done.

**Italy.** The comparator list for the 2025 to 2027 update is in the technical report, which has not been read. Unless it is found, Italy is marked not replicated, with the observation that the November 2024 update left betas unchanged.

**US panel.**
- The holding company's Value Line-style beta at each decision date: 5 years of weekly returns ending the Friday before the order month, against the S&P 500 (Value Line uses the NYSE Composite, which is not in the data), Blume-adjusted (0.67 raw + 0.33).
- AI-era contribution c = adjusted beta minus counterfactual adjusted beta (both counterfactuals), in beta units; it is zero for windows ending before 30 November 2022.
- Sample: consecutive in-panel decisions of the same rate unit. Outcome: change in authorised ROE (percentage points). Regressor: change in c. Controls: change in the 10-year Treasury yield and in the Baa spread, each as the mean over the 30 days before the order month. State fixed effects as specified, and the same regression without them. Standard errors clustered by state, with a wild cluster bootstrap.
- Reading: the coefficient is percentage points of ROE per unit of AI-era beta contribution, an effective market risk premium times the weight on CAPM. H3 predicts a positive coefficient below the full premium (about 5 to 6 points).

**H4.** Basis points times the equity share of the regulated asset base. US: the stated rate base where a filing gives it, otherwise the FERC net-plant proxy as an upper bound, and per customer with 2023 customers. UK: per £1 billion of regulatory asset value at 45% equity, because RIIO-3 asset values by company were not collected.
