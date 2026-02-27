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

**Phase 0 (Complete):** Variables (77 entries), Gaps (35 entries), and Traps (12 entries) migrated. Build pipeline operational.

**Phase 1 (Pending):** Observations, Scenarios, Sessions, Modules.

**Phase 2 (Pending):** Module prose content (ITB-A through ITB-H, ISA modules).

**Phase 3 (Pending):** Policy Briefs.

## Requirements

```bash
pip install pyyaml jsonschema jinja2
```

## See Also

- `CLAUDE_CODE_INSTRUCTIONS.md` — Operating manual for Claude Code
- `schemas/` — JSON Schema definitions for all entity types
- `scripts/` — One-time migration scripts from original markdown
