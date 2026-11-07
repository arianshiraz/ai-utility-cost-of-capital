# Rate-case coding notes

Notes on applying [ratecase_rule.md](ratecase_rule.md) to cases the rule does not spell out. Each note is dated and was written before the panel regression was run.

**7 November 2026: rehearing and compliance orders.** An order that changes rates but leaves the allowed return explicitly unchanged (for example, a rehearing that revisits rate base after the commission refused to revisit the return) is recorded with `in_panel = 0`. Only orders in which the commission decided the return enter the panel. Where a filing does not make clear whether the return was open, `in_panel` is set to `pending` until the commission's order is read.

**7 November 2026: statutory formula years.** For Illinois units before 2024, the formula years are recorded as a single regime row with `in_panel = 0`, as the rule excludes formula-rate annual updates.

**7 November 2026: dates.** Order and effective dates are recorded to the month when the filing gives only the month. Dockets are filled from the commission's own records.

**7 November 2026: extraction and verification.** `code/07_extract_ratecase_sentences.py` reads each filing from EDGAR in memory and keeps only sentences that state a return on equity; no filing is stored. `code/08_ratecase_candidates.py` turns those sentences into one candidate row per unit and return value (`output/tables/ratecase_candidates.csv`). Candidates are unverified: a sentence about a sister utility in another state can pass the filter. A value enters `data/classification/ratecase_decisions.csv` only after the order, its month and the return are confirmed in the filing text, with the quote recorded.

**7 November 2026: Ohio Power electric security plans.** Ohio Power's electric security plans set returns for riders, not base rates, so they are not recorded as decisions under the rule.

**8 November 2026: rate freezes and stay-outs.** Orders that freeze base rates or approve a stay-out (Wisconsin Electric 2017, NSP-Minnesota 2020) do not reset base rates and are recorded with `in_panel = 0`.

**8 November 2026: ranges and midpoints.** Where a commission sets a range (Florida Power & Light rate agreements, Georgia Power alternate rate plans, Entergy Louisiana's formula rate plan), the recorded return is the midpoint or the stated authorised value, and the range is given in `panel_note`.

**8 November 2026: California.** The California commission sets returns in separate cost of capital decisions, not in general rate cases. These decisions are recorded as the units' decisions. Changes made by the automatic cost of capital adjustment mechanism are formula updates and enter with `in_panel = 0`.

**8 November 2026: Entergy Louisiana.** Returns are set when the formula rate plan is renewed or extended; these renewals are recorded and enter the panel. Annual formula plan evaluations are excluded.

**8 November 2026: values read from a sentence window.** For a few rows the return sits in a sentence after the order sentence. These rows say so in `panel_note` and are rechecked first in the second pass.

**8 November 2026: sources outside the extracted filings.** Where the 10-K text did not give a value, three other primary sources were used: a 10-Q outside the extraction window (Alliant, filed 1 November 2024), a subsidiary's own 10-K (NSP-Minnesota, filed 26 February 2018), and commission orders on the regulator's letterhead (Wisconsin dockets 5-UR-110 and 5-UR-111). News reports were used only to locate decisions. One example of why: press coverage attached a 9.25% return to NSP-Minnesota's 2017 order, but the company's 10-K shows the June 2017 order at 9.2%; the 9.25% belongs to the July 2023 order.

**8 November 2026: settlements that keep the prior return.** A settlement that changes rates but states that the most recently approved return continues (OG&E, June 2018) is recorded with `in_panel = 0`, because the return was not re-decided.
