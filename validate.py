#!/usr/bin/env python3
"""
validate.py - Validate ITP YAML data files against JSON schemas.
Also checks cross-reference integrity across all entity types.

Usage:
    python validate.py                  # validate all
    python validate.py variables        # validate one entity type
    python validate.py --xref           # cross-reference check only
"""

import sys
import json
import yaml
from pathlib import Path
from jsonschema import validate, ValidationError

BASE = Path(__file__).parent
DATA = BASE / "data"
SCHEMAS = BASE / "schemas"

# Map entity type -> (data file, schema file, id field)
ENTITY_MAP = {
    "variables":    ("variables.yaml",    "variable.schema.json",    "id"),
    "gaps":         ("gaps.yaml",         "gap.schema.json",         "id"),
    "traps":        ("traps.yaml",        "trap.schema.json",        "id"),
    "observations": ("observations.yaml", "observation.schema.json", "id"),
    "scenarios":    ("scenarios.yaml",    "scenario.schema.json",    "id"),
    "sessions":     ("sessions.yaml",     "session.schema.json",     "number"),
    "modules":      ("modules.yaml",      "module.schema.json",      "code"),
}


def load_yaml(path: Path) -> list:
    """Load a YAML file, return list of entities."""
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return []
    if isinstance(data, dict) and "entries" in data:
        return data["entries"]
    if isinstance(data, list):
        return data
    return []


def load_schema(path: Path) -> dict:
    """Load a JSON schema file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_entity_type(entity_type: str) -> list:
    """Validate all entries for a given entity type. Returns list of errors."""
    if entity_type not in ENTITY_MAP:
        return [f"Unknown entity type: {entity_type}"]

    data_file, schema_file, id_field = ENTITY_MAP[entity_type]
    data_path = DATA / data_file
    schema_path = SCHEMAS / schema_file

    if not data_path.exists():
        return [f"Data file not found: {data_path}"]
    if not schema_path.exists():
        return [f"Schema file not found: {schema_path}"]

    entries = load_yaml(data_path)
    schema = load_schema(schema_path)
    errors = []

    # Check for duplicate IDs
    ids_seen = set()
    for entry in entries:
        eid = entry.get(id_field, "UNKNOWN")
        if eid in ids_seen:
            errors.append(f"  [{entity_type}] Duplicate ID: {eid}")
        ids_seen.add(eid)

    # Validate each entry against schema
    for i, entry in enumerate(entries):
        eid = entry.get(id_field, f"index-{i}")
        try:
            validate(instance=entry, schema=schema)
        except ValidationError as e:
            # Shorten the path for readability
            path_str = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "(root)"
            errors.append(f"  [{entity_type}] {eid}: {path_str}: {e.message}")

    return errors


def check_cross_references() -> list:
    """Check that cross-references between entities resolve."""
    errors = []

    # Load all entity IDs
    all_ids = {}
    for entity_type, (data_file, _, id_field) in ENTITY_MAP.items():
        entries = load_yaml(DATA / data_file)
        for entry in entries:
            eid = str(entry.get(id_field, ""))
            all_ids[f"{entity_type}:{eid}"] = True

    # Build quick lookup sets
    trap_ids = set()
    obs_ids = set()
    scenario_ids = set()
    module_codes = set()
    gap_ids = set()
    var_ids = set()

    for entries_data in [(DATA / "traps.yaml", "id"),
                         (DATA / "observations.yaml", "id"),
                         (DATA / "scenarios.yaml", "id"),
                         (DATA / "modules.yaml", "code"),
                         (DATA / "gaps.yaml", "id"),
                         (DATA / "variables.yaml", "id")]:
        path, field = entries_data
        for entry in load_yaml(path):
            val = str(entry.get(field, ""))
            if path.stem == "traps":
                trap_ids.add(val)
            elif path.stem == "observations":
                obs_ids.add(val)
            elif path.stem == "scenarios":
                scenario_ids.add(val)
            elif path.stem == "modules":
                module_codes.add(val)
            elif path.stem == "gaps":
                gap_ids.add(val)
            elif path.stem == "variables":
                var_ids.add(val)

    # For now, report counts rather than deep cross-ref checking
    # (Deep checking requires parsing prose cross_refs strings, which is Phase 2)
    print(f"\n  Cross-reference inventory:")
    print(f"    Traps:        {len(trap_ids)}")
    print(f"    Observations: {len(obs_ids)}")
    print(f"    Scenarios:    {len(scenario_ids)}")
    print(f"    Modules:      {len(module_codes)}")
    print(f"    Gaps:         {len(gap_ids)}")
    print(f"    Variables:    {len(var_ids)}")

    return errors


def main():
    args = sys.argv[1:]
    xref_only = "--xref" in args
    args = [a for a in args if a != "--xref"]

    types_to_check = args if args else list(ENTITY_MAP.keys())

    total_errors = []
    total_entries = 0

    if not xref_only:
        for entity_type in types_to_check:
            data_file = ENTITY_MAP.get(entity_type, (None,))[0]
            if data_file:
                entries = load_yaml(DATA / data_file)
                count = len(entries)
                total_entries += count
                errors = validate_entity_type(entity_type)
                if errors:
                    print(f"\n❌ {entity_type} ({count} entries): {len(errors)} error(s)")
                    for e in errors:
                        print(e)
                    total_errors.extend(errors)
                else:
                    print(f"✅ {entity_type} ({count} entries): OK")

    xref_errors = check_cross_references()
    total_errors.extend(xref_errors)

    print(f"\n{'='*50}")
    if total_errors:
        print(f"VALIDATION FAILED: {len(total_errors)} error(s) across {total_entries} entries")
        sys.exit(1)
    else:
        print(f"VALIDATION PASSED: {total_entries} entries across {len(types_to_check)} entity types")
        sys.exit(0)


if __name__ == "__main__":
    main()
