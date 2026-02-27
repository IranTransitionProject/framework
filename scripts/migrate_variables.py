#!/usr/bin/env python3
"""
migrate_variables.py - Parse APPENDIX_VARIABLES.md and extract to YAML.
One-time migration script.
"""

import re
import yaml
from pathlib import Path

SRC = Path("/mnt/project/APPENDIX_VARIABLES.md")
OUT = Path("/home/claude/itp-db/data/variables.yaml")


def clean_text(s: str) -> str:
    """Clean markdown formatting and mojibake."""
    s = s.strip()
    # Fix common mojibake patterns
    mojibake_map = {
        "\u00e2\u0080\u0093": "\u2013",  # en-dash
        "\u00e2\u0080\u0094": "\u2014",  # em-dash
        "\u00e2\u0080\u0099": "\u2019",  # right single quote
        "\u00e2\u0080\u009c": "\u201c",  # left double quote
        "\u00e2\u0080\u009d": "\u201d",  # right double quote
        "\u00c2\u00a7": "\u00a7",        # section sign
        "\u00c2\u00b3": "\u00b3",        # superscript 3
        "\u00e2\u0089\u00a4": "\u2264",  # less than or equal
        "\u00e2\u0086\u0092": "\u2192",  # right arrow
    }
    for bad, good in mojibake_map.items():
        s = s.replace(bad, good)
    # Remove leading/trailing ** for bold
    s = re.sub(r'^\*\*(.*)\*\*$', r'\1', s)
    return s


def extract_name_and_version(raw: str):
    """Extract variable name and version tag from the name column."""
    raw = raw.strip()
    # Pattern: **(v1.3)** **Name** or just **Name**
    version_match = re.search(r'\(v(\d+\.\d+)\)', raw)
    version = f"v{version_match.group(1)}" if version_match else "v1.0"

    # Remove version tag and bold markers
    name = re.sub(r'\*\*\(v\d+\.\d+\)\*\*\s*', '', raw)
    name = re.sub(r'\(v\d+\.\d+\)\s*', '', name)
    name = re.sub(r'\*\*', '', name)
    name = name.strip()
    return name, version


def parse_table_rows(lines: list, start_idx: int) -> list:
    """Parse markdown table rows starting from header row. Returns list of row tuples."""
    rows = []
    i = start_idx
    # Skip to first | row
    while i < len(lines) and not lines[i].strip().startswith('|'):
        i += 1
    if i >= len(lines):
        return rows
    # Skip header row
    i += 1
    # Skip separator row (| :--- | ...)
    if i < len(lines) and re.match(r'\|\s*:?-+', lines[i].strip()):
        i += 1

    # Parse data rows
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith('|'):
            break
        # Split by | and strip
        cells = [c.strip() for c in line.split('|')]
        # Remove empty first and last from leading/trailing |
        if cells and cells[0] == '':
            cells = cells[1:]
        if cells and cells[-1] == '':
            cells = cells[:-1]
        if cells:
            rows.append(cells)
        i += 1

    return rows


def assign_id(table: str, idx: int) -> str:
    """Assign a sequential ID based on table type."""
    prefix_map = {
        "stock": "SV",
        "flow": "FV",
        "threshold": "TV",
        "positive_optionality": "PO",
        "normalization_quality": "NQ",
    }
    prefix = prefix_map.get(table, "XX")
    if table == "normalization_quality":
        return f"NQ-{idx:02d}"
    return f"{prefix}-{idx:02d}"


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        lines = f.readlines()

    content = "".join(lines)
    variables = []

    # Find each table section
    current_table = None
    table_counters = {}

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect table headings
        if "TABLE 1:" in stripped or "CRITICAL STOCK VARIABLES" in stripped:
            current_table = "stock"
        elif "TABLE 2:" in stripped or "CRITICAL FLOW VARIABLES" in stripped:
            current_table = "flow"
        elif "TABLE 3:" in stripped or "THRESHOLD" in stripped:
            current_table = "threshold"
        elif "TABLE 4:" in stripped or "POSITIVE OPTIONALITY" in stripped:
            current_table = "positive_optionality"
        elif "NORMALIZATION QUALITY VARIABLES" in stripped:
            current_table = "normalization_quality"

        # Parse table rows when we hit a header row
        if current_table and stripped.startswith('| Variable') or stripped.startswith('| Code'):
            rows = parse_table_rows(lines, i)

            for row in rows:
                if current_table == "normalization_quality" and len(row) >= 5:
                    code = clean_text(row[0])
                    name = clean_text(row[1])
                    nq_type = clean_text(row[2])
                    desc = clean_text(row[3])
                    threshold = clean_text(row[4])

                    var = {
                        "id": code,
                        "name": name,
                        "table": "normalization_quality",
                        "current_value": "",
                        "trend": "",
                        "insight": desc,
                        "confidence": "Med",
                        "version_added": "v1.4",
                        "session_added": 12,
                        "cross_refs": [],
                        "epistemic_tag": "Mixed",
                        "nq_type": nq_type,
                        "nq_threshold": threshold,
                    }
                    variables.append(var)

                elif len(row) >= 5:
                    raw_name = row[0]
                    name, version = extract_name_and_version(raw_name)
                    name = clean_text(name)

                    # Skip empty names
                    if not name or name == "Variable":
                        continue

                    if current_table not in table_counters:
                        table_counters[current_table] = 0
                    table_counters[current_table] += 1
                    idx = table_counters[current_table]
                    vid = assign_id(current_table, idx)

                    var = {
                        "id": vid,
                        "name": name,
                        "table": current_table,
                        "current_value": clean_text(row[1]),
                        "trend": clean_text(row[2]),
                        "insight": clean_text(row[3]),
                        "confidence": clean_text(row[4]).strip("[]"),
                        "version_added": version,
                        "session_added": None,
                        "cross_refs": [],
                        "epistemic_tag": "Mixed",
                    }
                    variables.append(var)

            current_table = None  # Reset after parsing table

    # Extract monitoring notes from the bottom of the file
    monitoring_notes = []
    in_notes = False
    for line in lines:
        if line.strip().startswith("*Variables require") or line.strip().startswith("*v1."):
            in_notes = True
        if in_notes and line.strip().startswith("*"):
            note = clean_text(line.strip().strip("*"))
            if note:
                monitoring_notes.append(note)

    # Build output
    output = {
        "version": "1.7",
        "date": "2026-02-24",
        "source": "v1.5 + Session 15 (A12 variables) + Session 16 integration",
        "monitoring_notes": monitoring_notes if monitoring_notes else [
            "Variables require weekly recheck on flow and threshold tables. Stock variables recheck monthly or on significant event.",
            "v1.5 NOTE (CRITICAL): Trump deadline variables, Iran proposal delivery, Geneva Round 3 outcome, and student protest expansion require DAILY monitoring through at least March 6.",
            "v1.7 NOTE (Session 16): IAEA Board (March 2) creates third independent clock converging with Geneva Round 3 and Trump deadline."
        ],
        "entries": variables,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True, width=200, sort_keys=False)

    print(f"Migrated {len(variables)} variables to {OUT}")
    for table_name in ["stock", "flow", "threshold", "positive_optionality", "normalization_quality"]:
        count = sum(1 for v in variables if v["table"] == table_name)
        print(f"  {table_name}: {count}")


if __name__ == "__main__":
    main()
