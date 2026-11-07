# US rate-case sample and coding rule (decision D5)

**Status:** frozen on 7 November 2026, before any rate-case outcome was collected. Later changes are logged as dated amendments, with results reported under both versions.

## Purpose

The US panel test for H3 (pre-specification, section 4) regresses the change in each utility's authorised return on equity on the AI-era contribution to its replica beta. This rule fixes which decisions enter that panel, so that the sample cannot be chosen after seeing the outcomes.

## Sample: one rate unit for each of the 33 US holding companies

**Holding companies.** All 33 regulated electric utilities in the exposure sample (`output/tables/dc_exposure_candidates.csv`). None is dropped.

**Rate unit.** For each holding company, the (rate unit, state) pair with the largest electricity deliveries to ultimate customers in 2023.
- *Rate unit:* a consolidated electric operating subsidiary, or several sister subsidiaries whose base rates are set in one proceeding. Three such groups are combined: Evergy Kansas Central with Evergy Kansas South; Ohio Edison, Cleveland Electric Illuminating and Toledo Edison; and AEP Texas Central with AEP Texas North (merged in 2016). The map and its notes are in `data/classification/us_operating_utilities.csv`.
- *Consolidated:* subsidiaries accounted for by the equity method are excluded. Example: Sempra's 80% stake in Oncor.
- *Deliveries:* EIA-861 2023 megawatt-hours across all customer classes, counting bundled sales and delivery-only service (Parts A, C and D, plus EIA's delivery-company file for the Texas wires utilities). Energy-only sales by retail marketers (Part B) are excluded. Delivery-only volume counts because wires-only utilities (Commonwealth Edison, CenterPoint Houston) earn their allowed return on the network, not on the energy sold.
- *Why 2023:* it matches the FY2023 exposure vintage and is fixed before any AI-era outcome is examined.
- *Result:* `output/tables/ratecase_units.csv`, built by `code/06_select_ratecase_units.py`.

**Close calls.** In four holding companies the chosen unit leads the runner-up by less than 15%:
- Xcel: Northern States Power-Minnesota over Public Service Co of Colorado, 2.4%;
- Ameren: Ameren Illinois over Ameren Missouri, 9.7%;
- AEP: Ohio Power over AEP Texas, 12.0%;
- Otter Tail: Minnesota over North Dakota, 12.3%.

The rule is applied as written to these too.

## Which decisions are recorded

Every final order of the state commission, dated 1 January 2015 to 6 November 2026, that sets or resets base rates for the unit's electric service in its state. This includes commission-approved settlements.

For each decision, the following are recorded:
- the docket number and order date;
- the date the new rates took effect;
- the authorised return on equity, and the equity share of the capital structure;
- whether the decision was a settlement;
- the requested return on equity;
- the source and page.

**Not recorded as decisions:** rider and tracker updates, formula-rate annual updates that apply a return set elsewhere, interim rates, FERC transmission rates, and gas rates.

**Settlements without a stated return** ("black box" settlements) are recorded with the return marked as not stated, and they do not enter the regression. Their number is reported.

**Return adders** (for example performance incentives) are recorded separately from the base authorised return. The base return is the dependent variable.

## Sources, in order of preference

1. The commission's order.
2. The utility's own 10-K or 10-Q describing the order, with page. EDGAR is reachable by script, so every unit can be covered this way.
3. Trade press or industry summaries, used only to locate a decision, never as the recorded value.

Every value cites its source and page. A second pass re-checks each recorded return against the cited page.

## Known features of the sample, stated before collection

- **Illinois units (Commonwealth Edison, Ameren Illinois).** Under the Energy Infrastructure Modernization Act, distribution returns were set by a statutory formula tied to Treasury yields until multi-year rate plans began in 2024. The formula's exact terms are to be verified from the statute. Decisions under the formula carry no CAPM judgement and are flagged.
- **Texas wires utilities (CenterPoint Houston, Texas-New Mexico Power).** Full base rate cases are infrequent, so these units may contribute few decisions.
- **Settlements.** Black-box settlements are common in some states, and the number of usable decisions per unit will vary.

## Still open (for the pre-specification controls)

The bond-spread control in the US panel needs a public series in place of proprietary utility bond indices. One candidate is a BBB corporate option-adjusted spread from FRED, to be confirmed before use.
