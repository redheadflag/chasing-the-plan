from __future__ import annotations

import io
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.reports.assembler import PlanDoc, PlanRow, StageCell

FONT_DIR = Path(__file__).parent / "fonts"
FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"

_FONTS_READY = False

# Palette sampled from the sample plan.pdf.
CLR_RED = colors.HexColor("#F00000")     # day headers + "Примечание:"
CLR_BLUE = colors.HexColor("#0070C0")    # exercise names / links
CLR_GREEN = colors.HexColor("#60A830")   # "film this" exercises + legend
CLR_RULE = colors.HexColor("#C8C8C8")    # thin band separators
CLR_BLACK = colors.HexColor("#000000")

HEX_BLUE = "#0070C0"
HEX_GREEN = "#60A830"


def _ensure_fonts() -> None:
    global _FONTS_READY
    if _FONTS_READY:
        return
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(FONT_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, str(FONT_DIR / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFontFamily(FONT_REGULAR, normal=FONT_REGULAR, bold=FONT_BOLD)
    _FONTS_READY = True


def _styles() -> dict[str, ParagraphStyle]:
    return {
        "athlete": ParagraphStyle(
            "athlete", fontName=FONT_BOLD, fontSize=13, leading=16, textColor=CLR_BLACK
        ),
        "athlete_note": ParagraphStyle(
            "athlete_note", fontName=FONT_REGULAR, fontSize=9, leading=12,
            textColor=colors.HexColor("#666666"),
        ),
        "week": ParagraphStyle(
            "week", fontName=FONT_BOLD, fontSize=13, leading=16, textColor=CLR_BLACK
        ),
        "day": ParagraphStyle(
            "day", fontName=FONT_BOLD, fontSize=11, leading=14, textColor=CLR_RED
        ),
        "muscle": ParagraphStyle(
            "muscle", fontName=FONT_BOLD, fontSize=7.5, leading=10, textColor=CLR_BLACK
        ),
        "exercise": ParagraphStyle(
            "exercise", fontName=FONT_BOLD, fontSize=7.5, leading=10
        ),
        "stage": ParagraphStyle(
            "stage", fontName=FONT_REGULAR, fontSize=7, leading=8.5, alignment=1
        ),
        "note": ParagraphStyle(
            "note", fontName=FONT_REGULAR, fontSize=7.5, leading=10, textColor=CLR_BLACK
        ),
        "notes_head": ParagraphStyle(
            "notes_head", fontName=FONT_BOLD, fontSize=8.5, leading=12, textColor=CLR_RED
        ),
        "notes_body": ParagraphStyle(
            "notes_body", fontName=FONT_REGULAR, fontSize=8, leading=12,
            textColor=CLR_BLACK,
        ),
        "legend": ParagraphStyle(
            "legend", fontName=FONT_REGULAR, fontSize=8, leading=11, textColor=CLR_GREEN
        ),
    }


def _exercise_para(row: PlanRow, style: ParagraphStyle) -> Paragraph:
    name = escape(row.exercise_name)
    color = HEX_GREEN if row.highlight else HEX_BLUE
    if row.exercise_url:
        url = escape(row.exercise_url, {'"': "&quot;"})
        inner = f'<a href="{url}" color="{color}">{name}</a>'
    else:
        inner = f'<font color="{color}">{name}</font>'
    return Paragraph(inner, style)


def _stage_cell(stage: StageCell, width: float, style: ParagraphStyle) -> Table:
    """A fraction-style cell: value over a thin rule over the set count.

    The rule matches the text colour and is narrower than the cell (centred),
    while the value/series text keep the full width so they never wrap.
    """
    rule = HRFlowable(
        width="72%", thickness=0.4, color=CLR_BLACK, hAlign="CENTER",
        spaceBefore=0, spaceAfter=0,
    )
    return Table(
        [
            [Paragraph(escape(stage.top), style)],
            [rule],
            [Paragraph(escape(stage.bottom), style)],
        ],
        colWidths=[width],
        style=TableStyle(
            [
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                # Symmetric gap between the rule and the text above / below it.
                ("TOPPADDING", (0, 1), (0, 1), 1),
                ("BOTTOMPADDING", (0, 1), (0, 1), 1),
            ]
        ),
    )


def _group_bands(rows: list[PlanRow]) -> list[list[PlanRow]]:
    bands: list[list[PlanRow]] = []
    for row in rows:
        if bands and bands[-1][0].band_id == row.band_id:
            bands[-1].append(row)
        else:
            bands.append([row])
    return bands


def render_pdf(doc: PlanDoc) -> bytes:
    _ensure_fonts()
    st = _styles()

    margin = 0.3 * inch
    page_w = letter[0]
    usable = page_w - 2 * margin

    n = doc.max_stages
    mg_w, note_w, stage_w = 80.0, 132.0, 56.0
    ex_w = usable - mg_w - note_w - stage_w * n
    if ex_w < 110:
        stage_w = 44.0
        ex_w = usable - mg_w - note_w - stage_w * n
    if ex_w < 90:
        note_w = 120.0
        ex_w = usable - mg_w - note_w - stage_w * n
    if ex_w < 70:
        ex_w = 70.0
    col_widths = [mg_w, ex_w] + [stage_w] * n + [note_w]
    note_col = 2 + n

    flow: list = []

    prev_week: int | None = None
    for day in doc.days:
        if doc.multi_week and day.week != prev_week:
            if prev_week is not None:
                flow.append(Spacer(1, 6))
            flow.append(Paragraph(f"Неделя {day.week}", st["week"]))
            flow.append(
                HRFlowable(
                    width="100%", thickness=1, color=CLR_BLACK,
                    spaceBefore=2, spaceAfter=5,
                )
            )
            prev_week = day.week

        flow.append(Paragraph(escape(day.title), st["day"]))
        flow.append(Spacer(1, 3))

        data: list[list] = []
        style_cmds: list = [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (0, -1), 0),
            # A wider gap before the note (comment) text.
            ("LEFTPADDING", (note_col, 0), (note_col, -1), 14),
        ]

        # Superset blocks get a black rule immediately before and after them.
        # Two adjacent supersets share the boundary rule (no doubled line).
        line_rows: set[int] = set()
        for band in _group_bands(day.rows):
            start = len(data)
            for i, row in enumerate(band):
                is_first = i == 0
                cells: list = [
                    Paragraph(escape(row.muscle_group), st["muscle"]),
                    _exercise_para(row, st["exercise"]),
                ]
                for s in range(n):
                    if s < len(row.stages):
                        cells.append(_stage_cell(row.stages[s], stage_w - 4, st["stage"]))
                    else:
                        cells.append("")
                # Note column: unit note, plus block note on the first superset row.
                note_text = escape(row.note or "")
                if is_first and row.is_superset and row.block_note:
                    bn = escape(row.block_note)
                    note_text = f"{note_text}<br/>{bn}" if note_text else bn
                cells.append(Paragraph(note_text, st["note"]))
                data.append(cells)
            if band[0].is_superset:
                line_rows.add(start)      # rule before the superset
                line_rows.add(len(data))  # rule after the superset

        n_rows = len(data)
        for k in line_rows:
            if k >= n_rows:
                style_cmds.append(
                    ("LINEBELOW", (0, n_rows - 1), (-1, n_rows - 1), 0.75, CLR_BLACK)
                )
            else:
                style_cmds.append(("LINEABOVE", (0, k), (-1, k), 0.75, CLR_BLACK))

        if data:
            flow.append(
                Table(data, colWidths=col_widths, style=TableStyle(style_cmds))
            )

        if day.notes:
            flow.append(Spacer(1, 5))
            flow.append(Paragraph("Примечание:", st["notes_head"]))
            for line in day.notes.splitlines():
                if line.strip():
                    flow.append(Paragraph(escape(line), st["notes_body"]))
        flow.append(Spacer(1, 16))

    if any(row.highlight for day in doc.days for row in day.rows):
        flow.append(
            Paragraph(
                "Зелёным цветом выделены упражнения, которые нужно снять на видео.",
                st["legend"],
            )
        )

    # Size the page height to the content so there is no trailing white space.
    content_h = 0.0
    for f in flow:
        content_h += f.wrap(usable, 1_000_000)[1]
    page_h = content_h + 2 * margin + 6  # + small safety buffer

    buffer = io.BytesIO()
    pdf = BaseDocTemplate(
        buffer,
        pagesize=(page_w, page_h),
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title="План тренировок",
    )
    frame = Frame(
        margin, margin, usable, page_h - 2 * margin,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    pdf.addPageTemplates([PageTemplate(id="plan", frames=[frame])])
    pdf.build(flow)
    return buffer.getvalue()
