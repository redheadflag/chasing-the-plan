"""Parse samples/exercises.xlsx into a bulk-import .http request.

The sample sheet is a matrix: row 1 holds muscle-group names (column headers),
and each column below lists the exercise names for that group. This script turns
that into `seed/exercises.http`, a single idempotent POST to /api/exercises/bulk
that a REST client (VS Code REST Client, JetBrains .http, or `httpie`) can replay.

Usage:
    python seed/generate_seed_http.py
"""

from __future__ import annotations

import json
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "samples" / "exercises.xlsx"
OUTPUT = ROOT / "seed" / "exercises.http"


def parse_exercises() -> list[dict[str, str | None]]:
    # Load WITHOUT data_only so cell.hyperlink is available (exercise URLs are
    # stored as hyperlinks on the name cells).
    wb = openpyxl.load_workbook(SOURCE)
    ws = wb.worksheets[0]
    grid = list(ws.iter_rows())  # cell objects, so we can read .hyperlink
    if not grid:
        return []

    header_row = grid[0]
    items: list[dict[str, str | None]] = []
    seen: set[tuple[str, str]] = set()

    for col, header_cell in enumerate(header_row):
        header = header_cell.value
        group = str(header).strip() if header is not None else ""
        if not group:
            continue
        for row in grid[1:]:
            if col >= len(row):
                continue
            cell = row[col]
            if cell.value is None:
                continue
            name = str(cell.value).strip()
            # Skip blanks, single-char section markers, and rows echoing the header.
            if len(name) <= 1 or name == group:
                continue
            key = (group, name)
            if key in seen:
                continue
            seen.add(key)
            url = cell.hyperlink.target if cell.hyperlink else None
            items.append({"muscle_group": group, "name": name, "url": url})

    return items


def main() -> None:
    items = parse_exercises()
    body = {"create_missing_groups": True, "items": items}
    payload = json.dumps(body, ensure_ascii=False, indent=2)

    content = (
        "@baseUrl = http://localhost:8000\n\n"
        "### Seed muscle groups + exercises from the sample workbook.\n"
        "### Idempotent: re-running skips anything already present.\n"
        "POST {{baseUrl}}/api/exercises/bulk\n"
        "Content-Type: application/json\n\n"
        f"{payload}\n"
    )
    OUTPUT.write_text(content, encoding="utf-8")

    groups = sorted({item["muscle_group"] for item in items})
    with_url = sum(1 for i in items if i["url"])
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    print(f"  {len(items)} exercises across {len(groups)} muscle groups")
    print(f"  {with_url} of them have a URL (from cell hyperlinks)")
    print(f"  groups: {', '.join(groups)}")


if __name__ == "__main__":
    main()
