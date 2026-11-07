"""Build data/project_data_workbook.xlsx: every dataset gathered so far, with sources.

Run after stages 01 to 03. Values taken from sources are blue; computed cells are Excel
formulas (black). Recalculate in Excel (or LibreOffice) before reading cached values.
"""
from datetime import date

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from config import ROOT, TABLES, UTILITIES

OUT = ROOT / "data" / "project_data_workbook.xlsx"
CLS = ROOT / "data" / "classification"
FONT = "Arial"
HEAD_FILL = PatternFill("solid", start_color="1F3864")
BLUE = "0000FF"


def style_header(ws, ncol: int) -> None:
    for c in range(1, ncol + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"


def write_table(ws, df: pd.DataFrame, widths: dict | None = None, wrap: set | None = None,
                url_cols: set | None = None, input_font: bool = True) -> None:
    ws.append(list(df.columns))
    for row in df.itertuples(index=False):
        ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in row])
    style_header(ws, len(df.columns))
    for r in range(2, ws.max_row + 1):
        for c in range(1, len(df.columns) + 1):
            cell = ws.cell(row=r, column=c)
            col = df.columns[c - 1]
            cell.font = Font(name=FONT, color=BLUE if input_font else "000000")
            cell.alignment = Alignment(wrap_text=bool(wrap and col in wrap), vertical="top")
            if url_cols and col in url_cols and isinstance(cell.value, str) and cell.value.startswith("http"):
                cell.hyperlink = cell.value
                cell.font = Font(name=FONT, color=BLUE, underline="single")
    for i, col in enumerate(df.columns, start=1):
        ws.column_dimensions[get_column_letter(i)].width = (widths or {}).get(col, 16)
    ws.auto_filter.ref = ws.dimensions


def readme(wb: Workbook) -> None:
    ws = wb.active
    ws.title = "README"
    lines = [
        ("Does the AI Boom Raise Utilities' Cost of Capital? Data workbook", True),
        (f"Built {date.today().isoformat()} by code/09_build_workbook.py from the files in data/ and output/tables/.", False),
        ("Rebuild: python code/09_build_workbook.py (after the data stages). Do not edit by hand; edit the source CSV files instead.", False),
        ("", False),
        ("Legend", True),
        ("Blue text: values taken from a source (regulator document, SEC filing, data provider).", False),
        ("Black text: Excel formulas computed from other cells.", False),
        ("Evidence 'primary': read in the regulator's or company's own document, page cited. 'secondary': from summaries or search results, still to confirm.", False),
        ("", False),
        ("Sheets", True),
    ]
    sheets = [
        ("Decisions", "Design decisions D1 to D5, proposals P1 to P5 and the exposure-vintage decision, with dates."),
        ("Utilities", "The 65 listed utilities by country and role (regulated, placebo, merchant, mixed)."),
        ("Price_Coverage", "Daily price series from Yahoo Finance: first and last date and number of observations."),
        ("Regulator_Methods", "How each regulator sets the return on equity: beta source, window, frequency, adjustment, timing."),
        ("Regulator_Parameters", "Numerical parameters from each decision (risk-free rate, betas, gearing, allowed returns)."),
        ("Ofgem_Comparator_Betas", "Asset betas of Ofgem's nine comparators over 2, 5 and 10 years (Draft Determinations, Table 16)."),
        ("DC_Exposure", "Data-centre mentions per 10,000 words of each US utility's main 10-K, FY2023 and FY2024."),
        ("DC_MW_Sentences", "Sentences in 10-K and 8-K filings pairing data centres with an MW or GW figure."),
        ("DC_Share_Sentences", "10-K sentences pairing data centres with a percentage (for share-of-sales coding)."),
        ("DC_SEC_Documents", "Every SEC document retrieved by the data-centre search, with links."),
        ("Yields_Coverage", "National 10-year government bond yields (rate factor): source series, first and last date, observations, mean."),
        ("Hub_Flags_NonUS", "Whether each non-US network firm serves a national data-centre hub, with reason and source."),
        ("RateCase_Units", "The rate unit chosen for each US holding company (largest 2023 deliveries, EIA-861), with runner-up and margin."),
        ("US_Operating_Utilities", "Each holding company's consolidated electric operating utilities, EIA numbers and rate-unit groupings."),
    ]
    for text, bold in lines:
        ws.append([text])
        ws.cell(row=ws.max_row, column=1).font = Font(name=FONT, bold=bold, size=12 if bold else 10)
    for name, desc in sheets:
        ws.append([name, desc])
        ws.cell(row=ws.max_row, column=1).font = Font(name=FONT, bold=True)
        ws.cell(row=ws.max_row, column=2).font = Font(name=FONT)
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 110


def decisions(wb: Workbook) -> None:
    rows = [
        ("D1", "Countries", "Core six: US, UK, Germany, Spain, Italy, Canada; Australia and Japan descriptive only", "2026-11-07", "Decided"),
        ("D2", "Regulator methods", "Extracted for all six from primary documents where accessible (see Regulator_Methods)", "2026-11-07", "Done; US Value Line and Canada formulas still secondary"),
        ("D3", "Currency", "Local currency throughout; SMH converted at daily FX and orthogonalised to the local index", "2026-11-07", "Decided"),
        ("D4", "Data-centre exposure", "10-K text intensity (revised after collection); MW and share of sales descriptive", "2026-11-07", "Frozen (docs/exposure_rule.md)"),
        ("D5", "US allowed returns", "All 33 US holding companies; one rate unit each (largest 2023 deliveries); every base-rate order 2015 to 2026 (docs/ratecase_rule.md)", "2026-11-07", "Decided; rule drafted, awaiting freeze"),
        ("P1 to P5", "Design proposals", "Continuous exposure to AI-era betas; cross-border comparators; exposure vs composition channels; UK placebo overlap; Germany from 2029", "2026-11-07", "Adopted"),
        ("Vintage", "Exposure vintage", "FY2023 primary (mentions per 10k words; any-mention indicator secondary); FY2024 in ranks as robustness; both reported in every table", "2026-11-07", "Decided"),
        ("Pre-spec", "Pre-specification of all tests", "Hypotheses, estimators, windows, inference and robustness fixed before any returns are analysed", "2026-11-07", "Frozen (docs/prespecification.md)"),
        ("Index", "Market indices", "UK: FTSE All-Share (^FTAS) as pre-specified. Germany: CDAX not on Yahoo Finance, DAX used instead (substitution recorded)", "2026-11-07", "Recorded"),
        ("Rates IT", "Italian rate factor", "No official daily Italian 10-year yield found (Bank of Italy benchmark series is monthly). Candidate: ECB daily euro-area 10-year yield on all government bonds; monthly changes correlate 0.84 with the Italian yield. Main: ECB series; robustness: German Bund", "2026-11-07", "Adopted (pre-specification, Amendment 1)"),
        ("Exposure non-US", "Country data-centre share", "IEA publishes data-centre electricity by region, not for the UK, Germany, Spain, Italy or Canada. Non-US exposure is the hub flag alone (Hub_Flags_NonUS)", "2026-11-07", "Adopted (pre-specification, Amendment 2)"),
    ]
    ws = wb.create_sheet("Decisions")
    write_table(ws, pd.DataFrame(rows, columns=["id", "topic", "decision", "date", "status"]),
                widths={"decision": 90, "topic": 22, "status": 40}, wrap={"decision", "status"})


def dc_exposure(wb: Workbook) -> None:
    c = pd.read_csv(TABLES / "dc_exposure_candidates.csv")
    names = pd.read_csv(UTILITIES).set_index("ticker")["name"]
    w = c.pivot(index="ticker", columns="vintage", values=["dc_mentions", "tenk_words", "any_mw"])
    order = c.drop_duplicates("ticker")["ticker"]
    ws = wb.create_sheet("DC_Exposure")
    head = ["ticker", "name", "mentions FY2023", "10-K words FY2023", "per 10k words FY2023",
            "mentions FY2024", "10-K words FY2024", "per 10k words FY2024",
            "change in per 10k (FY2024 minus FY2023)", "rank FY2023", "rank FY2024",
            "MW sentence found FY2023", "MW sentence found FY2024"]
    ws.append(head)
    n = len(order)
    last = n + 1
    for i, t in enumerate(order, start=2):
        ws.append([t, names.get(t, ""),
                   int(w.loc[t, ("dc_mentions", "FY2023")]), int(w.loc[t, ("tenk_words", "FY2023")]),
                   f"=IF(D{i}>0,C{i}/D{i}*10000,0)",
                   int(w.loc[t, ("dc_mentions", "FY2024")]), int(w.loc[t, ("tenk_words", "FY2024")]),
                   f"=IF(G{i}>0,F{i}/G{i}*10000,0)",
                   f"=H{i}-E{i}",
                   f"=RANK(E{i},$E$2:$E${last})", f"=RANK(H{i},$H$2:$H${last})",
                   int(w.loc[t, ("any_mw", "FY2023")]), int(w.loc[t, ("any_mw", "FY2024")])])
    style_header(ws, len(head))
    for r in range(2, last + 1):
        for col in range(1, len(head) + 1):
            is_formula = col in (5, 8, 9, 10, 11)
            ws.cell(row=r, column=col).font = Font(name=FONT, color="000000" if is_formula else BLUE)
        for col in (5, 8, 9):
            ws.cell(row=r, column=col).number_format = "0.00;-0.00;-"
    s = last + 2
    summary = [
        ("Firms mentioning data centres, FY2023", f'=COUNTIF(C2:C{last},">0")'),
        ("Firms mentioning data centres, FY2024", f'=COUNTIF(F2:F{last},">0")'),
        ("Firms in sample", f"=COUNTA(A2:A{last})"),
        ("Correlation of per-10k measures across vintages (Pearson)", f"=CORREL(E2:E{last},H2:H{last})"),
    ]
    for k, (label, formula) in enumerate(summary):
        ws.cell(row=s + k, column=1, value=label).font = Font(name=FONT, bold=True)
        cell = ws.cell(row=s + k, column=5, value=formula)
        cell.font = Font(name=FONT)
        cell.number_format = "0.00"
    note = s + len(summary) + 1
    notes = [
        "Source: main 10-K document of each utility filed in the window (FY2023: Jan to Mar 2024; FY2024: Jan to Mar 2025), SEC EDGAR filing index; counts by code/03_dc_exposure_measures.py.",
        "Spearman rank correlation across vintages computed in Python: 0.53 (see the stage 03 output).",
        "Mentions count matches of 'data center(s)' or 'data centre(s)'. Zero means the main 10-K does not mention data centres.",
    ]
    for k, text in enumerate(notes):
        ws.cell(row=note + k, column=1, value=text).font = Font(name=FONT, italic=True)
    widths = [8, 26, 11, 13, 13, 11, 13, 13, 16, 9, 9, 12, 12]
    for i, wd in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = wd
    ws.row_dimensions[1].height = 45


def ofgem_betas(wb: Workbook) -> None:
    b = pd.read_csv(CLS / "ofgem_dd_comparator_betas.csv")
    ws = wb.create_sheet("Ofgem_Comparator_Betas")
    head = list(b.columns) + ["2-year minus 10-year"]
    ws.append(head)
    for i, row in enumerate(b.itertuples(index=False), start=2):
        vals = [None if (isinstance(v, float) and pd.isna(v)) else v for v in row]
        ws.append(vals + [f'=IF(OR(D{i}="",F{i}=""),"",D{i}-F{i})'])
    style_header(ws, len(head))
    last = ws.max_row
    for r in range(2, last + 1):
        for c in range(1, len(head) + 1):
            ws.cell(row=r, column=c).font = Font(name=FONT, color="000000" if c == len(head) else BLUE)
        for c in range(4, len(head) + 1):
            ws.cell(row=r, column=c).number_format = "0.00"
    ws.cell(row=last + 2, column=1, value="Mean of comparators").font = Font(name=FONT, bold=True)
    for c, col in zip(range(4, 7), "DEF"):
        cell = ws.cell(row=last + 2, column=c, value=f"=AVERAGE({col}2:{col}{last})")
        cell.font = Font(name=FONT)
        cell.number_format = "0.00"
    ws.cell(row=last + 4, column=1, value=(
        "Source: Ofgem, RIIO-3 Draft Determinations Finance Annex (July 2025), p56, Table 16, asset betas at "
        "0.075 debt beta; https://www.ofgem.gov.uk/sites/default/files/2025-06/Draft-Determinations-Finance-Annex.pdf. "
        "The Final Determinations (Dec 2025, p55) keep the asset beta at 0.375 from a range of 0.30 to 0.45 covering "
        "the 10-year values.")).font = Font(name=FONT, italic=True)
    for i, wd in enumerate([24, 9, 8, 13, 13, 13, 16], start=1):
        ws.column_dimensions[get_column_letter(i)].width = wd


def regulator_parameters(wb: Workbook) -> None:
    p = pd.read_csv(CLS / "regulator_parameters.csv")
    ws = wb.create_sheet("Regulator_Parameters")
    write_table(ws, p, widths={"decision": 18, "parameter": 44, "unit": 22, "source_url": 40,
                               "note": 50, "regulator": 10, "page_ref": 9},
                wrap={"parameter", "note"}, url_cols={"source_url"})
    vcol = list(p.columns).index("value") + 1
    for r, unit in enumerate(p["unit"], start=2):
        ws.cell(row=r, column=vcol).number_format = "0.000" if unit in ("beta", "share") else "0.00%"


def main() -> None:
    wb = Workbook()
    readme(wb)
    decisions(wb)
    write_table(wb.create_sheet("Utilities"), pd.read_csv(UTILITIES),
                widths={"name": 28, "role": 20, "note": 60}, wrap={"note"})
    write_table(wb.create_sheet("Price_Coverage"), pd.read_csv(TABLES / "data_coverage.csv"))
    write_table(wb.create_sheet("Regulator_Methods"), pd.read_csv(CLS / "regulator_methods.csv"),
                widths={c: 28 for c in ["decision", "capm_role", "beta_source", "window", "frequency",
                                        "adjustment", "reestimation", "regime_for_h3", "source_url",
                                        "page_refs"]},
                wrap={"decision", "capm_role", "beta_source", "window", "frequency", "adjustment",
                      "reestimation", "regime_for_h3", "page_refs"},
                url_cols={"source_url"})
    regulator_parameters(wb)
    ofgem_betas(wb)
    dc_exposure(wb)
    write_table(wb.create_sheet("DC_MW_Sentences"), pd.read_csv(TABLES / "dc_snippets.csv"),
                widths={"sentence": 110, "url": 40}, wrap={"sentence"}, url_cols={"url"})
    write_table(wb.create_sheet("DC_Share_Sentences"), pd.read_csv(TABLES / "dc_share_sentences.csv"),
                widths={"sentence": 120}, wrap={"sentence"})
    write_table(wb.create_sheet("DC_SEC_Documents"), pd.read_csv(TABLES / "dc_documents.csv"),
                widths={"url": 90}, url_cols={"url"})
    write_table(wb.create_sheet("Yields_Coverage"), pd.read_csv(TABLES / "yields_coverage.csv"),
                widths={"series": 80})
    write_table(wb.create_sheet("Hub_Flags_NonUS"), pd.read_csv(CLS / "hub_flags_nonus.csv"),
                widths={"name": 20, "reason": 80, "source_url": 60, "evidence_and_notes": 40},
                wrap={"reason", "source_url", "evidence_and_notes"})
    write_table(wb.create_sheet("RateCase_Units"), pd.read_csv(TABLES / "ratecase_units.csv"),
                widths={"operating_utility": 45, "eia_name": 45, "runner_up": 45})
    write_table(wb.create_sheet("US_Operating_Utilities"), pd.read_csv(CLS / "us_operating_utilities.csv"),
                widths={"operating_utility": 40, "rate_unit": 50, "rate_unit_note": 60, "note": 50, "evidence": 50},
                wrap={"rate_unit_note", "note", "evidence"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
