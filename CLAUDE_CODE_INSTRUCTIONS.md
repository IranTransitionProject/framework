# ITP Database: Claude Code Operating Instructions

## Architecture

The Iran Transition Project data is stored as **YAML data files** validated against **JSON Schema** definitions. Markdown reports are **generated artifacts** — never edit them directly.

```
itp-db/
├── data/                    # SOURCE OF TRUTH
│   ├── variables.yaml       # APP-V dashboard (77 entries)
│   ├── gaps.yaml            # APP-G research gaps (35 entries)
│   ├── traps.yaml           # ISA-TRAPS simultaneity traps (12 entries)
│   ├── observations.yaml    # ISA-SCENARIOS observations (future)
│   ├── scenarios.yaml       # ISA-SCENARIOS scenarios (future)
│   ├── sessions.yaml        # Session log (future)
│   └── modules.yaml         # Module registry (future)
│
├── schemas/                 # VALIDATION RULES
│   ├── variable.schema.json
│   ├── gap.schema.json
│   ├── trap.schema.json
│   ├── observation.schema.json
│   ├── scenario.schema.json
│   ├── session.schema.json
│   └── module.schema.json
│
├── templates/               # REPORT TEMPLATES (Jinja2)
│   ├── app_variables.md.j2
│   ├── app_gaps.md.j2
│   └── (future: isa_traps.md.j2, isa_scenarios.md.j2, master_index.md.j2)
│
├── output/                  # GENERATED MARKDOWN (never edit)
│   ├── APPENDIX_VARIABLES.md
│   └── APPENDIX_GAPS.md
│
├── scripts/                 # MIGRATION SCRIPTS (one-time use)
│   ├── migrate_variables.py
│   ├── migrate_gaps.py
│   └── cleanup_variables.py
│
├── validate.py              # Schema validation + cross-ref check
├── build.py                 # YAML → Markdown renderer
└── CLAUDE_CODE_INSTRUCTIONS.md  # This file
```

## Core Rules

### Rule 1: Never edit output/*.md files
These are generated. Edit the YAML source, then rebuild.

### Rule 2: Validate before every commit
```bash
python validate.py          # all entity types
python validate.py variables  # one type
```

### Rule 3: Build after every data change
```bash
python build.py             # all reports
python build.py variables   # one report
python build.py --validate  # validate then build
```

### Rule 4: Atomic updates
Change one field in one entity per operation. The build propagates cross-references.

## Common Operations

### Add a new variable
```yaml
# Append to data/variables.yaml entries list:
- id: SV-19       # Next sequential ID for stock table
  name: "New Variable Name"
  table: stock     # stock | flow | threshold | positive_optionality | normalization_quality
  current_value: "value"
  trend: "direction"
  insight: "analytical significance"
  confidence: "Med"
  version_added: "v1.8"
  session_added: 18
  cross_refs: ["ITB-A10", "ISA-TRAPS Trap 8"]
  epistemic_tag: Inference
```

### Update an existing variable
Find by `id` in `data/variables.yaml`, change the relevant field:
```yaml
# Change current_value for SV-01:
- id: SV-01
  current_value: "87 (Khamenei)"  # was "86 (Khamenei)"
```

### Add a new gap
```yaml
# Append to data/gaps.yaml entries list:
- id: G17-01
  description: "What information is missing"
  priority: 1          # 1=Critical, 2=Important, 3=Useful, 4=Enrichment
  status: OPEN         # OPEN | PARTIALLY_FILLED | FILLED | DEPRIORITIZED | ELEVATED
  modules: ["ITB-B"]
  why_critical: "Why this matters"
  blocking_for: ["ISA-TRAPS Trap 2"]
  session_identified: 17
  cross_refs: []
```

### Fill a gap
```yaml
# Find gap by id, change:
  status: FILLED
  session_filled: 17
  fill_note: "How it was resolved"
```

### Change gap priority
```yaml
# Find gap by id, change:
  priority: 1     # was 2
  status: ELEVATED
```

### Add a new trap
```yaml
# Append to data/traps.yaml entries list:
- id: 13                      # Next sequential integer
  title: "Short Descriptive Title"
  category: negotiation_deal   # core_transition | negotiation_deal
  session_added: 18
  confidence: "[Inference -- Med]"
  mechanism: >-
    How the trap operates (prose).
  circular_structure: >-
    A requires B --> B requires C --> C requires A.
  resolution_path: >-
    How to break the circularity.
  detection_signal: "What to monitor"
  historical_parallels:
    - case: "Country -- Event"
      lesson: "What this case teaches"
  extensions:
    - version: "v1.0"
      session: 18
      title: "Extension title"
      content: "Additional analysis added later"
  itb_anchors: ["ITB-A10", "ITB-F"]
  cross_refs: ["Trap 8", "Obs 012"]
```

### Add an extension to an existing trap
```yaml
# Find trap by id, append to extensions array:
  extensions:
    # ... existing extensions ...
    - version: "v2.4"
      session: 18
      title: "New dimension"
      content: "New analysis to append"
```

### Update metadata (version, date)
Edit the top-level fields in the YAML file:
```yaml
version: "1.8"
date: "2026-02-26"
source: "v1.7 + Session 17 integration"
```

## ID Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Stock variable | `SV-NN` | SV-01, SV-18 |
| Flow variable | `FV-NN` | FV-01, FV-24 |
| Threshold variable | `TV-NN` | TV-01, TV-15 |
| Positive optionality | `PO-NN` | PO-01, PO-10 |
| Normalization quality | `NQ-NN` | NQ-01, NQ-10 |
| Session gap | `GNN-NN` | G12-01, G16-04 |
| Legacy gap | `gap-slug` | gap-artesh-loyalty |
| Trap | integer | 1, 12 |
| Observation | integer | 1, 21 |
| Scenario | `S{n}{letter?}` | S1, S1A, S1B, S2 |

## Schema Validation Rules

Each entity type has a JSON Schema in `schemas/`. Key constraints:

- **Variables:** `id` must match `^(SV|FV|TV|PO|NQ)-\d{2}$`
- **Gaps:** `id` must match `^(G\d{2}-\d{2}|G16-\d{2}|gap-[a-z0-9-]+)$`
- **Gaps:** `priority` must be 1-4 (integer)
- **Gaps:** `status` must be one of: OPEN, PARTIALLY_FILLED, FILLED, DEPRIORITIZED, ELEVATED, CONFLICT
- All entities require specific fields (see schema `required` arrays)

## Integration Spec → Database Updates

When a Claude session produces an Integration Spec (the current delivery format), translate it to database operations:

1. **New variables:** Append entries to `data/variables.yaml`
2. **Updated variables:** Find by ID, update changed fields
3. **New gaps:** Append entries to `data/gaps.yaml`
4. **Filled gaps:** Update status + session_filled + fill_note
5. **Version bump:** Update metadata version/date/source
6. **Validate:** `python validate.py`
7. **Build:** `python build.py`
8. **Commit:** `git add -A && git commit -m "Session N: [summary]"`

## Future Migration (Phase 1-3)

Phase 0 (current): Variables + Gaps migrated. Pipeline proven.

Phase 1: Migrate Traps, Observations, Scenarios, Sessions, Modules.
- These have more narrative prose content mixed with structured data
- Prose sections stored as `content` string fields in YAML
- Templates handle rendering

Phase 2: Migrate module prose content (ITB-A through ITB-H, ISA-CORE).
- Each module becomes a YAML file in `data/content/`
- Sections[] array with prose blocks + metadata

Phase 3: Migrate Briefs.
- Structured changelog, findings, version history
- Body prose as content blocks

## Mojibake Handling

The original markdown files contain UTF-8 mojibake (double-encoded characters). The migration scripts include cleanup functions, but some artifacts may remain. When found:

1. Fix in the YAML source data
2. Do NOT fix in output/*.md (it will be overwritten)
3. Common patterns:
   - `â€"` → `—` (em-dash)
   - `â€"` → `–` (en-dash)
   - `Â§` → `§` (section sign)
