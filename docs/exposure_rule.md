# Data-centre exposure coding rule (decision D4)

**Status:** frozen on 7 November 2026, after the first collection and before any utility returns were analysed. The rule in force is "Revision after collection" below; the original draft that follows it is kept for the record. Later changes are logged as dated amendments, as in the DeepSeek study's classification rule.

## Revision after collection (7 November 2026)

Collection showed that megawatt pipelines are mostly published in earnings presentations on company websites, which are not filed with the SEC for many utilities (Dominion is one example) and are not consistently archived. In SEC filings, only 6 of 33 utilities pair data centres with an MW figure in the FY2024 vintage. The draft MW measure therefore cannot be built consistently. The revised rule:

- **Source:** each utility's main 10-K document filed in the vintage window, taken from the SEC filing index (not exhibits), plus 8-K exhibits filed in the same window for MW sentences.
- **Primary measure:** data-centre mentions per 10,000 words of the main 10-K (zero if none). Text-based exposure measures from firm disclosures are an established approach; the specific precedents (for example Hassan, Hollander, van Lent and Tahoun on political risk, and Sautner, van Lent, Vilkov and Zhang on climate change exposure) are to be verified before citing.
- **Secondary, descriptive:** any MW figure, and any data-centre share of sales (for example Dominion: data centres were 26% of Virginia Power's 2024 electricity sales and 24% of 2023's).
- **Both vintages reported in every table:** FY2023 (10-Ks filed January to March 2024) and FY2024 (filed January to March 2025). One is named primary before any returns are analysed; the other is reported alongside as robustness.
- **Vintage decision (7 November 2026): FY2023 is primary.** It is set before most AI-era returns, which answers the objection that exposure reacted to stock prices. The measures used in the tests are:
  1. primary: FY2023 data-centre mentions per 10,000 words (no outliers: maximum 0.98);
  2. secondary: FY2023 indicator, 1 if the main 10-K mentions data centres at all (10 of 33 firms);
  3. robustness: FY2024 intensity in ranks, because one firm (NiSource, 3.38) dominates the FY2024 values in levels.
- **Results of the collection** (`output/tables/dc_exposure_candidates.csv`): 10 of 33 utilities mention data centres in the FY2023 10-K and 24 of 33 in FY2024; Spearman rank correlation between vintages 0.53.

The sections below are the original draft, kept for the record.

## Purpose

Hypotheses H1 and H2 predict larger AI-related changes in co-movement and beta for utilities more exposed to data-centre demand. This rule fixes how exposure is measured, so the measure cannot be tuned to the results.

## United States: firm-level measure

**Source.** Each utility's own investor materials for fiscal year 2024: the Q4 2024 earnings presentation, the earnings call transcript, and the FY2024 10-K, all published between 1 January and 31 March 2025. Using one fixed vintage for every firm avoids picking whichever disclosure looks largest.

**What is counted.** Megawatts of data-centre or large-load demand that the utility reports as:
1. signed (electric service agreements, letters of agreement, contracts), and
2. advanced (engineering studies complete, construction agreements, or the utility's own "high-probability" category).

Requests that are only inquiries or early-stage queue entries are recorded separately and not counted in the primary measure.

**Scaling.** Primary exposure = (signed + advanced MW) ÷ the utility's 2024 system peak load (MW), from the 10-K or EIA-861. For holding companies with several operating utilities, MW and peak load are summed across operating utilities.

**Zero.** A utility that reports no data-centre or large-load pipeline in any of the three sources is coded zero, with a note that nothing was found.

**Secondary measures.**
- Total pipeline including early-stage requests, scaled the same way.
- A hub indicator: 1 if the utility serves a recognised data-centre hub (Northern Virginia, Columbus Ohio, Dallas Fort Worth, Phoenix, Atlanta, Chicago, Silicon Valley), else 0.

**Recording.** `data/classification/dc_exposure_us.csv`: ticker, MW signed, MW advanced, MW early-stage, peak load, measure, source document, page or slide, quote of the figure, collector's note.

## Outside the United States: country-level measure with a firm adjustment

There are too few listed regulated utilities outside the US for firm-level pipelines to add much, and disclosure practices differ by country.

**Primary.** Data-centre share of national electricity demand in 2024, from one consistent source (IEA, *Energy and AI*, 2025) for every country.

**Firm adjustment (where documentable).** 1 if the firm's regulated network serves a national data-centre hub, else 0, with the source:

| Country | Hub | Listed firms and likely coding (to verify) |
|---|---|---|
| United Kingdom | London and Slough | SSE (its southern distribution network covers the Slough area): 1; National Grid (transmission nationwide; its distribution networks are in the Midlands, South West and Wales): 0 |
| Germany | Frankfurt | E.ON: verify which distribution subsidiaries serve the Frankfurt region |
| Spain | Madrid | Redeia (national transmission) and Enagás (gas): 0; Iberdrola: verify |
| Italy | Milan | Terna (national transmission): 0; Snam and Italgas (gas): 0 |
| Canada | Toronto and Montreal | Hydro One (Ontario): verify |

Transmission system operators that cover a whole country are coded 0 on the firm adjustment and carry the country-level measure only.

## Rules that apply everywhere

- One collector pass, then a second pass that re-checks every non-zero entry against the cited page.
- Any judgement call is written in the notes column at the time, not afterwards.
- The measure is fixed before any utility's returns are analysed after 30 November 2022.
