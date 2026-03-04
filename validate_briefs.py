#!/usr/bin/env python3
"""Validate brief YAML files against brief.schema.json."""

import json
import sys
from pathlib import Path

# jsonschema may need install
try:
    import jsonschema
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "jsonschema", "--break-system-packages", "-q"])
    import jsonschema

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "pyyaml", "--break-system-packages", "-q"])
    import yaml


BASE = Path(__file__).resolve().parent
SCHEMA_PATH = BASE / "schemas" / "brief.schema.json"
BRIEFS_DIR = BASE / "data" / "briefs"


def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_brief(filepath: Path, schema: dict) -> list[str]:
    """Validate a single brief YAML. Returns list of error strings (empty = pass)."""
    errors = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if data is None:
        return ["Empty YAML file"]

    # Schema validation
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        path_str = " → ".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"  [{path_str}] {err.message}")

    # Cross-validation: brief_id consistency with filename
    expected_prefix = filepath.stem.lower()
    actual_id = data.get("brief_id", "").lower()
    # b03 -> B03, eb01 -> EB01, etc.
    if expected_prefix.startswith("b") and not expected_prefix.startswith("eb"):
        expected_id = f"B{expected_prefix[1:].zfill(2)}"
    elif expected_prefix.startswith("eb"):
        expected_id = f"EB{expected_prefix[2:].zfill(2)}"
    elif expected_prefix == "intro":
        expected_id = "INTRO"
    elif expected_prefix in ("es", "exec_summary"):
        expected_id = "ES"
    elif expected_prefix.startswith("supp_"):
        expected_id = f"SUPP-{expected_prefix[5:].upper()}"
    else:
        expected_id = None

    if expected_id and data.get("brief_id") != expected_id:
        errors.append(f"  brief_id '{data.get('brief_id')}' does not match "
                       f"filename '{filepath.stem}' (expected '{expected_id}')")

    # Numbered brief must have number; non-numbered must have null
    bid = data.get("brief_id", "")
    num = data.get("number")
    if bid.startswith("B") and not bid.startswith("B0") == False:
        # It's a numbered brief if it matches B##
        if bid.startswith("B") and len(bid) == 3 and bid[1:].isdigit():
            if num is None:
                errors.append(f"  Numbered brief {bid} must have 'number' set")

    return errors


def main():
    schema = load_schema()
    yaml_files = sorted(BRIEFS_DIR.glob("*.yaml"))

    if not yaml_files:
        print(f"No YAML files found in {BRIEFS_DIR}")
        sys.exit(1)

    total_errors = 0
    for fp in yaml_files:
        errors = validate_brief(fp, schema)
        if errors:
            print(f"FAIL: {fp.name}")
            for e in errors:
                print(e)
            total_errors += len(errors)
        else:
            print(f"PASS: {fp.name}")

    print(f"\n{'='*40}")
    print(f"Files: {len(yaml_files)} | Errors: {total_errors}")

    if total_errors:
        sys.exit(1)
    else:
        print("All briefs valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
