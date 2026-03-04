#!/usr/bin/env python3
"""Build markdown briefs from YAML data using Jinja2 templates."""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "pyyaml", "--break-system-packages", "-q"])
    import yaml

try:
    import jinja2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "jinja2", "--break-system-packages", "-q"])
    import jinja2


BASE = Path(__file__).resolve().parent
BRIEFS_DIR = BASE / "data" / "briefs"
TEMPLATES_DIR = BASE / "templates"
OUTPUT_DIR = BASE / "output"


# Map brief types to template files
TEMPLATE_MAP = {
    "brief": "brief.md.j2",
    "emergency_brief": "brief.md.j2",
    "supplemental": "brief.md.j2",
    "executive_summary": "brief.md.j2",
    "introduction": "brief.md.j2",
}

# Map brief_id to output filename
def output_filename(data: dict) -> str:
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


def build_brief(yaml_path: Path, env: jinja2.Environment) -> tuple[str, str]:
    """Build a single brief. Returns (output_filename, rendered_markdown)."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    btype = data.get("type", "brief")
    template_name = TEMPLATE_MAP.get(btype, "brief.md.j2")

    try:
        template = env.get_template(template_name)
    except jinja2.TemplateNotFound:
        print(f"WARNING: Template '{template_name}' not found for {yaml_path.name}, "
              f"falling back to brief.md.j2")
        template = env.get_template("brief.md.j2")

    # Add display-formatted date only if not already in YAML
    if not data.get("date_display"):
        data["date_display"] = format_date_display(
            data.get("date_published") or data.get("date", "")
        )

    rendered = template.render(brief=data)

    # Clean up excessive blank lines (more than 2 consecutive)
    import re
    rendered = re.sub(r'\n{3,}', '\n\n', rendered)
    # Ensure file ends with single newline
    rendered = rendered.strip() + "\n"

    fname = output_filename(data)
    return fname, rendered


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build brief markdown from YAML")
    parser.add_argument("--validate", action="store_true",
                        help="Run validation before building")
    parser.add_argument("files", nargs="*",
                        help="Specific YAML files to build (default: all)")
    args = parser.parse_args()

    if args.validate:
        import subprocess
        result = subprocess.run([sys.executable,
                                 str(BASE / "validate_briefs.py")])
        if result.returncode != 0:
            print("\nValidation failed. Fix errors before building.")
            sys.exit(1)
        print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )

    if args.files:
        yaml_files = [Path(f) for f in args.files]
    else:
        yaml_files = sorted(BRIEFS_DIR.glob("*.yaml"))

    if not yaml_files:
        print(f"No YAML files found in {BRIEFS_DIR}")
        sys.exit(1)

    built = 0
    for fp in yaml_files:
        try:
            fname, rendered = build_brief(fp, env)
            out_path = OUTPUT_DIR / fname
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(rendered)
            print(f"BUILT: {fp.name} -> {fname}")
            built += 1
        except Exception as e:
            print(f"ERROR: {fp.name} -> {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*40}")
    print(f"Built {built}/{len(yaml_files)} briefs -> {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
