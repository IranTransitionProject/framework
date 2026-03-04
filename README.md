# Iran Transition Project — Structured Database

## What This Is

A relational database architecture for the Iran Transition Project (ITP), replacing hand-edited markdown files with structured YAML data validated against JSON schemas. Markdown reports are generated artifacts.

## Quick Start

```bash
# Validate all data
python validate.py

# Build all markdown reports + content + briefs
python build.py

# Validate then build
python build.py --validate

# Build specific targets
python build.py variables   # one report
python build.py content     # content modules only
python build.py briefs      # briefs only
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

**Phase 3 (Complete):** Convergence Briefs migrated to `data/briefs/` YAML files.
- Schema: `schemas/brief.schema.json`
- Template: `templates/brief.md.j2` (all brief types)
- Additional templates: `brief_changelog.md.j2`, `brief_governance.md.j2`
- 14 briefs migrated, validated, and building (10 numbered + 1 emergency + 1 exec summary + 1 intro + 1 supplemental)
- Integrated into unified `validate.py` and `build.py` pipeline

**Totals:** 190 structured entries + 19 content modules + 14 briefs = 38 generated markdown outputs

## Requirements

```bash
pip install pyyaml jsonschema jinja2 ftfy
```

## See Also

- `CLAUDE_CODE_INSTRUCTIONS.md` — Operating manual for Claude Code
- `schemas/` — JSON Schema definitions for all entity types
- `scripts/` — One-time migration scripts from original markdown
