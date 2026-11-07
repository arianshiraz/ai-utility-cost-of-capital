# Rate-case coding notes

Notes on applying [ratecase_rule.md](ratecase_rule.md) to cases the rule does not spell out. Each note is dated and was written before the panel regression was run.

**7 November 2026: rehearing and compliance orders.** An order that changes rates but leaves the allowed return explicitly unchanged (for example, a rehearing that revisits rate base after the commission refused to revisit the return) is recorded with `in_panel = 0`. Only orders in which the commission decided the return enter the panel. Where a filing does not make clear whether the return was open, `in_panel` is set to `pending` until the commission's order is read.

**7 November 2026: statutory formula years.** For Illinois units before 2024, the formula years are recorded as a single regime row with `in_panel = 0`, as the rule excludes formula-rate annual updates.

**7 November 2026: dates.** Order and effective dates are recorded to the month when the filing gives only the month. Dockets are filled from the commission's own records.

**7 November 2026: extraction and verification.** `code/07_extract_ratecase_sentences.py` reads each filing from EDGAR in memory and keeps only sentences that state a return on equity; no filing is stored. `code/08_ratecase_candidates.py` turns those sentences into one candidate row per unit and return value (`output/tables/ratecase_candidates.csv`). Candidates are unverified: a sentence about a sister utility in another state can pass the filter. A value enters `data/classification/ratecase_decisions.csv` only after the order, its month and the return are confirmed in the filing text, with the quote recorded.

**7 November 2026: Ohio Power electric security plans.** Ohio Power's electric security plans set returns for riders, not base rates, so they are not recorded as decisions under the rule.
