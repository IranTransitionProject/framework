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

import re
import sys
import yaml
from pathlib import Path
from datetime import date
from jinja2 import Environment, FileSystemLoader

BASE = Path(__file__).parent
DATA = BASE / "data"
CONTENT = DATA / "content"
BRIEFS = DATA / "briefs"
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


# --- Brief building helpers (Phase 3) ---

BRIEF_TEMPLATE_MAP = {
    "brief": "brief.md.j2",
    "emergency_brief": "brief.md.j2",
    "supplemental": "brief.md.j2",
    "executive_summary": "brief.md.j2",
    "introduction": "brief.md.j2",
}


def brief_output_filename(data: dict) -> str:
    """Derive output markdown filename from brief data."""
    bid = data.get("brief_id", "")
    btype = data.get("type", "brief")

    if btype == "executive_summary":
        return "00_Convergence_Briefs_-_Executive_Summary.md"
    elif btype == "introduction":
        return "01_Convergence_Briefs_-_Introduction.md"
    elif bid.startswith("EB"):
        title_slug = data.get("title", "").replace(" ", "_")
        title_slug = re.sub(r'[^A-Za-z0-9_-]', '', title_slug)
        return f"Emergency_Brief_{title_slug}_v2.md"
    elif bid.startswith("SUPP"):
        title_slug = data.get("title", "").replace(" ", "_")
        title_slug = re.sub(r'[^A-Za-z0-9_-]', '', title_slug)
        return f"{title_slug}.md"
    else:
        num = data.get("number", 0)
        title_slug = data.get("title", "").replace(" ", "_")
        title_slug = re.sub(r'[^A-Za-z0-9_-]', '', title_slug)
        return f"Brief_{num:02d}_{title_slug}.md"


def format_date_display(date_str: str) -> str:
    """Convert 2026-02-21 to February 2026 for display."""
    if not date_str or len(date_str) < 7:
        return date_str or ""
    months = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    parts = date_str.split("-")
    month = months.get(parts[1], parts[1])
    return f"{month} {parts[0]}"


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
        "index_meta": load_yaml(DATA / "index_meta.yaml") if (DATA / "index_meta.yaml").exists() else {},
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
        # Allow "content" and "briefs" as targets
        build_content = "content" in targets
        build_briefs = "briefs" in targets
        reports = {k: v for k, v in reports.items() if k in targets}
    else:
        build_content = True
        build_briefs = True

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

    # Build content modules (Phase 2)
    if build_content and CONTENT.exists():
        content_template_file = "module_content.md.j2"
        tmpl_path = TEMPLATES / content_template_file
        if not tmpl_path.exists():
            print(f"⚠️  Content template not found: {tmpl_path} — skipping content modules")
        else:
            template = env.get_template(content_template_file)
            # Find the output filename from modules.yaml registry
            modules_lookup = {m["code"]: m for m in ctx["modules"]}

            for yaml_file in sorted(CONTENT.glob("*.yaml")):
                with open(yaml_file, "r", encoding="utf-8") as f:
                    module_data = yaml.safe_load(f)
                if module_data is None:
                    continue

                mc = module_data.get("module_code", "")
                # Determine output filename from modules registry, or derive from code
                if mc in modules_lookup:
                    output_file = modules_lookup[mc].get("file", "").split("+")[0].strip().strip("`")
                else:
                    # Fallback: derive from module_code
                    output_file = mc.replace("-", "_") + ".md"

                rendered = template.render(module=module_data, **ctx)
                out_path = OUTPUT / output_file
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(rendered)
                print(f"✅ Built {output_file} ({len(rendered)} chars) [content: {mc}]")

    # Build briefs (Phase 3)
    if build_briefs and BRIEFS.exists():
        # Use a separate Jinja2 environment for briefs (different trim settings)
        brief_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES)),
            keep_trailing_newline=True,
            trim_blocks=False,
            lstrip_blocks=False,
        )

        for yaml_file in sorted(BRIEFS.glob("*.yaml")):
            with open(yaml_file, "r", encoding="utf-8") as f:
                brief_data = yaml.safe_load(f)
            if brief_data is None:
                continue

            btype = brief_data.get("type", "brief")
            template_name = BRIEF_TEMPLATE_MAP.get(btype, "brief.md.j2")

            try:
                template = brief_env.get_template(template_name)
            except Exception:
                print(f"⚠️  Template '{template_name}' not found for {yaml_file.name}, "
                      f"falling back to brief.md.j2")
                template = brief_env.get_template("brief.md.j2")

            # Add display-formatted date if not already set
            if not brief_data.get("date_display"):
                brief_data["date_display"] = format_date_display(
                    brief_data.get("date_published") or brief_data.get("date", "")
                )

            rendered = template.render(brief=brief_data)

            # Clean up excessive blank lines
            rendered = re.sub(r'\n{3,}', '\n\n', rendered)
            rendered = rendered.strip() + "\n"

            fname = brief_output_filename(brief_data)
            out_path = OUTPUT / fname
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(rendered)
            print(f"✅ Built {fname} ({len(rendered)} chars) [brief: {brief_data.get('brief_id', '?')}]")


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
