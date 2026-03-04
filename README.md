# Iran Transition Project — Structured Database

## What This Is

A relational database architecture for the Iran Transition Project (ITP), replacing hand-edited markdown files with structured YAML data validated against JSON schemas. Markdown reports are generated artifacts.

## Quick Start

```bash
# Validate all data
python validate.py

# Build all markdown reports
python build.py

# Validate then build
python build.py --validate

# Build specific report
python build.py variables
```

## Why

The original project accumulated 21+ markdown files updated via manual patch instructions from LLM sessions. This caused:
- Line number drift between sessions
- Inconsistent formatting across patches
- No schema validation on data integrity
- Cross-reference breakage as modules grew
- Compounding errors with each session

The database architecture solves these by making the YAML the single source of truth, with deterministic rendering to markdown.

## Current Status

**Phase 0 (Complete):** Variables (77 entries), Gaps (35 entries) migrated. Build pipeline operational.

**Phase 1 (Complete):** Traps (12), Observations (21), Scenarios (7), Sessions (13), Modules (25) migrated. All 190 entries validate. ISA-SCENARIOS and ISA-TRAPS templates built and tested.

**Phase 2 (Complete):** Module prose content migrated to `data/content/` YAML files.
- Schema: `schemas/content.schema.json`
- Template: `templates/module_content.md.j2` (generic for all modules)
- Master index: `templates/master_index.md.j2` + `data/index_meta.yaml`
- All 19 modules migrated, validated, and building
- Migration script: `scripts/migrate_content.py` (uses ftfy for mojibake repair)

**Phase 3 (Pending):** Policy Briefs.
- Session starter: `PHASE_3_SESSION_STARTER.md` (schema design, template plan, migration order)
- 12 briefs + 5 supporting documents
- Separate `brief.schema.json` (briefs have different structure: narrative prose, byline, update notes, companion list, governance metadata)
- 4 templates planned: brief, exec summary, changelog, governance

## Requirements

```bash
pip install pyyaml jsonschema jinja2 ftfy
```

## See Also

- `CLAUDE_CODE_INSTRUCTIONS.md` — Operating manual for Claude Code
- `schemas/` — JSON Schema definitions for all entity types
- `scripts/` — One-time migration scripts from original markdown
