#!/usr/bin/env python3
"""
build.py - Render ITP YAML data into markdown reports via Jinja2 templates.

Usage:
    python build.py                # build all outputs
    python build.py variables      # build one report
    python build.py --validate     # validate then build

Output goes to output/ directory. These are the generated reports
that replace hand-edited markdown files.
"""

import sys
import yaml
from pathlib import Path
from datetime import date
from jinja2 import Environment, FileSystemLoader

BASE = Path(__file__).parent
DATA = BASE / "data"
TEMPLATES = BASE / "templates"
OUTPUT = BASE / "output"


def load_yaml(path: Path):
    """Load YAML, return entries list."""
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return []
    if isinstance(data, dict):
        return data  # return full dict for metadata access
    return data


def load_entries(path: Path) -> list:
    """Load YAML, extract entries list."""
    data = load_yaml(path)
    if isinstance(data, dict) and "entries" in data:
        return data["entries"]
    if isinstance(data, list):
        return data
    return []


def load_metadata(path: Path) -> dict:
    """Load YAML, extract top-level metadata (everything except entries)."""
    data = load_yaml(path)
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k != "entries"}
    return {}


def build_all(env, targets=None):
    """Build all (or specified) output reports."""
    # Load all data
    ctx = {
        "variables": load_entries(DATA / "variables.yaml"),
        "variables_meta": load_metadata(DATA / "variables.yaml"),
        "gaps": load_entries(DATA / "gaps.yaml"),
        "gaps_meta": load_metadata(DATA / "gaps.yaml"),
        "traps": load_entries(DATA / "traps.yaml"),
        "traps_meta": load_metadata(DATA / "traps.yaml"),
        "observations": load_entries(DATA / "observations.yaml"),
        "observations_meta": load_metadata(DATA / "observations.yaml"),
        "scenarios": load_entries(DATA / "scenarios.yaml"),
        "scenarios_meta": load_metadata(DATA / "scenarios.yaml"),
        "sessions": load_entries(DATA / "sessions.yaml"),
        "modules": load_entries(DATA / "modules.yaml"),
        "build_date": date.today().isoformat(),
    }

    # Helpers for templates
    def filter_by(items, key, value):
        return [i for i in items if i.get(key) == value]

    def sort_by(items, key, reverse=False):
        return sorted(items, key=lambda x: x.get(key, ""), reverse=reverse)

    env.globals["filter_by"] = filter_by
    env.globals["sort_by"] = sort_by

    # Report map: target_name -> (template, output_file)
    reports = {
        "variables":    ("app_variables.md.j2",    "APPENDIX_VARIABLES.md"),
        "gaps":         ("app_gaps.md.j2",         "APPENDIX_GAPS.md"),
        "traps":        ("isa_traps.md.j2",        "ISA_TRAPS.md"),
        "scenarios":    ("isa_scenarios.md.j2",     "ISA_SCENARIOS.md"),
        "index":        ("master_index.md.j2",      "00_MASTER_INDEX.md"),
    }

    if targets:
        reports = {k: v for k, v in reports.items() if k in targets}

    OUTPUT.mkdir(exist_ok=True)

    for name, (template_file, output_file) in reports.items():
        tmpl_path = TEMPLATES / template_file
        if not tmpl_path.exists():
            print(f"⚠️  Template not found: {tmpl_path} — skipping {name}")
            continue

        template = env.get_template(template_file)
        rendered = template.render(**ctx)

        out_path = OUTPUT / output_file
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        print(f"✅ Built {output_file} ({len(rendered)} chars)")


def main():
    args = sys.argv[1:]

    do_validate = "--validate" in args
    args = [a for a in args if a != "--validate"]

    if do_validate:
        import subprocess
        result = subprocess.run([sys.executable, str(BASE / "validate.py")],
                                capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            print("Validation failed — aborting build.")
            sys.exit(1)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )

    targets = args if args else None
    build_all(env, targets)
    print(f"\n{'='*50}")
    print(f"Build complete. Output in: {OUTPUT}")


if __name__ == "__main__":
    main()
