# ITP Database: Claude Code Operating Instructions

## Architecture

The Iran Transition Project data is stored as **YAML data files** validated against
**JSON Schema** definitions. Markdown and PDF outputs are **generated artifacts** —
never edit them directly.

```
framework/
├── .github/workflows/       # CI configuration
│
├── data/                    # SOURCE OF TRUTH
│   ├── variables.yaml       # APP-V dashboard (86 entries)
│   ├── gaps.yaml            # APP-G research gaps (57 entries)
│   ├── traps.yaml           # ISA-TRAPS analytical traps (14 entries)
│   ├── observations.yaml    # Project observations (30 entries)
│   ├── scenarios.yaml       # Scenario matrix (12 entries)
│   ├── sessions.yaml        # Session log (20 entries)
│   ├── modules.yaml         # Module registry (28 entries)
│   ├── index_meta.yaml      # Master index semi-static content
│   ├── content/             # MODULE PROSE (22 modules)
│   │   ├── itb_a.yaml
│   │   ├── itb_b.yaml
│   │   └── ... (one file per module)
│   └── briefs/              # CONVERGENCE BRIEFS (17 files)
│       ├── b01.yaml - b13.yaml  # Numbered briefs
│       ├── eb01.yaml            # Emergency Brief
│       ├── es.yaml              # Executive Summary
│       ├── intro.yaml           # Introduction
│       └── supp_psc.yaml        # Supplemental
│
├── schemas/                 # VALIDATION RULES (9 schemas)
│   ├── variable.schema.json
│   ├── gap.schema.json
│   ├── trap.schema.json
│   ├── observation.schema.json
│   ├── scenario.schema.json
│   ├── session.schema.json
│   ├── module.schema.json
│   ├── content.schema.json
│   └── brief.schema.json
│
├── templates/               # REPORT TEMPLATES (Jinja2)
│   ├── app_variables.md.j2
│   ├── app_gaps.md.j2
│   ├── isa_traps.md.j2
│   ├── isa_scenarios.md.j2
│   ├── master_index.md.j2
│   ├── module_content.md.j2
│   ├── brief.md.j2
│   ├── brief_changelog.md.j2
│   └── brief_governance.md.j2
│
├── scripts/                 # MIGRATION SCRIPTS (one-time use, archived)
│   ├── migrate_variables.py
│   ├── migrate_gaps.py
│   ├── migrate_content.py
│   ├── migrate_all_briefs.py
│   ├── migrate_b03.py
│   └── cleanup_variables.py
│
├── output/                  # GENERATED MARKDOWN (gitignored — never edit)
├── releases/                # GENERATED PDFs (gitignored — attach to GitHub Releases)
├── staging/                 # Chat → Code content staging (gitignored)
│
├── validate.py              # Schema validation: entities + content modules
├── validate_briefs.py       # Schema validation: briefs
├── build.py                 # YAML → Markdown: entity reports + content modules
├── build_briefs.py          # YAML → Markdown: convergence briefs
├── build_pdf.py             # Markdown → PDF: two-tier release bundles
├── ARCHITECTURE.md          # Database design and pipeline documentation
├── README.md                # Project overview and quickstart
├── CONTRIBUTING.md          # Contribution standards and CLA
├── GOVERNANCE.md            # Mission constraint and succession plan
├── CLAUDE_SESSION_LOG.md    # Claude-to-Claude coordination log
├── CLAUDE_CHAT_INSTRUCTIONS.md  # Chat-side operating instructions
├── SUBMISSIONS.md           # Community submissions protocol (DRAFT)
├── RELEASE_NOTES_TEMPLATE.md
├── LICENSE
└── CLAUDE_CODE_INSTRUCTIONS.md  # This file
```

---

## Core Rules

### Rule 1: Never edit output/*.md files
These are generated artifacts. Edit the YAML source, then rebuild.

### Rule 2: Validate before every commit
```bash
python validate.py              # entities + content modules
python validate_briefs.py       # briefs
python validate.py variables    # single entity type
```

### Rule 3: Build after every data change
```bash
python build.py                 # entity reports + content modules
python build_briefs.py          # convergence briefs
python build.py variables       # one report only
python build.py content         # content modules only
python build.py --validate      # validate then build
```

### Rule 4: Atomic updates
Change one field in one entity per operation. The build propagates cross-references.

---

## Common Operations

### Add a new variable
```yaml
# Append to data/variables.yaml entries list:
- id: SV-19       # Next sequential ID for this table type
  name: "New Variable Name"
  table: stock     # stock | flow | threshold | positive_optionality | normalization_quality
  current_value: "value"
  trend: "direction"
  insight: "analytical significance"
  confidence: "Med"
  version_added: "v1.9"
  session_added: 21
  cross_refs: ["ITB-A10", "ISA-TRAPS Trap 8"]
  epistemic_tag: Inference
```

### Update an existing variable
```yaml
# Find by id in data/variables.yaml, change the relevant field:
- id: SV-01
  current_value: "new value"   # was "old value"
```

### Add a new gap
```yaml
# Append to data/gaps.yaml entries list:
- id: G21-01
  description: "What information is missing"
  priority: 1          # 1=Critical, 2=Important, 3=Useful, 4=Enrichment
  status: OPEN         # OPEN | PARTIALLY_FILLED | FILLED | DEPRIORITIZED | ELEVATED | CONFLICT
  modules: ["ITB-B"]
  why_critical: "Why this matters for decisions"
  blocking_for: ["ISA-TRAPS Trap 2"]
  session_identified: 21
  cross_refs: []
```

### Fill a gap
```yaml
# Find gap by id, update:
  status: FILLED
  session_filled: 21
  fill_note: "How it was resolved"
```

### Change gap priority
```yaml
# Find gap by id, update:
  priority: 1     # was 2
  status: ELEVATED
```

### Add a new observation
```yaml
# Append to data/observations.yaml entries list:
- id: 31                    # Next sequential integer
  title: "Short Descriptive Title"
  diagnosis: >-
    What is true (analytical finding).
  strategic_implication: >-
    What this means for planning.
  itb_anchors: ["ITB-A10", "ISA-TRAPS Trap 8"]
  scenario_impact:
    W1: "How this affects Scenario W1"
  leading_indicators:
    - "What to monitor"
  corrections:
    - session: 21
      date: "2026-03-05"
      content: "What changed and why"
  sources: ["Source"]
  cross_refs: ["Obs 010"]
  confidence: "[Inference -- Med]"
  version_added: "v1.7"
  session_added: 21
```

### Add a new trap
```yaml
# Append to data/traps.yaml entries list:
- id: 15                      # Next sequential integer
  title: "Short Descriptive Title"
  category: negotiation_deal   # core_transition | negotiation_deal
  session_added: 21
  confidence: "[Inference -- Med]"
  mechanism: >-
    How the trap operates.
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
      session: 21
      title: "Extension title"
      content: "Additional analysis"
  itb_anchors: ["ITB-A10", "ITB-F"]
  cross_refs: ["Trap 8", "Obs 012"]
```

### Add an extension to an existing trap
```yaml
# Find trap by id, append to extensions array:
  extensions:
    # ... existing extensions ...
    - version: "v2.5"
      session: 21
      title: "New dimension"
      content: "New analysis to append"
```

### Update a scenario probability
```yaml
# Find scenario by id, update:
  probability_current: "40-55%"
  probability_history:
    # ... existing entries ...
    - version: "v2.0"
      range: "40-55%"
      rationale: "Why the probability changed"
```

### Add a new session
```yaml
# Append to data/sessions.yaml entries list:
- number: 22
  date: "2026-03-05"
  summary: "What was accomplished"
  modules_affected: ["ITB-A", "ISA-SCENARIOS"]
```

### Add a new module to the registry
```yaml
# Append to data/modules.yaml entries list:
- code: "ITB-A13"
  file: "ITB_A13_New_Module.md"
  version: "1.0"
  lines_approx: "~200"
  description: "What this module covers"
  level: 1
  dependencies: ["ITB-A"]
```

### Add a new content module
```yaml
# Create data/content/itb_a13.yaml:
module_code: ITB-A13          # Must match modules.yaml code
version: "1.0"
date: "2026-03-05"
source: "Session 22"
dependencies: ["ITB-A"]
referenced_by: []
title: "New Module Title"
pillar: "A"
last_verified: "2026-03-05"
confidence: "Med"
sections:
  - id: "A13.1"
    title: "First Section"
    level: 2
    content: |
      Markdown prose. Supports bullets, tables, inline tags.
      * **Key finding:** Example. [Fact — Med]
    subsections:
      - id: "A13.1.1"
        title: "Subsection"
        level: 3
        tags: ["NEW"]
        content: |
          Subsection prose.
footer: >-
  Remaining gaps: what is not yet covered.
```

### Update a content module section
```yaml
# In data/content/itb_b.yaml, find section by id:
  - id: "B1"
    title: "Updated Title"
    content: |
      Updated prose here...
```

### Add a new brief
```yaml
# Create data/briefs/b14.yaml:
brief_id: B14
number: 14
title: "Brief Title"
subtitle: "Optional Subtitle"
author: "Hooman Mehr"
contact: "hooman@mac.com"
series_link: "https://hmehr.substack.com/p/iran-the-convergence-briefs"
version: "v1.0"
date: "2026-03-05"
date_published: "2026-03-05"
status: DRAFT
type: brief
core_thesis: "Single-sentence thesis statement."
itb_anchors: ["ITB-A", "ITB-B"]
sections:
  - title: "First Section"
    content: |
      Markdown prose here.
source_summary: "~N English and Farsi sources"
companion_briefs:
  - number: 1
    title: "The Blind Spot in Every Iran Deal"
    link: "https://hmehr.substack.com/p/the-blind-spot"
author_bio: "Author bio text"
```

### Update a brief section
```yaml
# In data/briefs/b01.yaml, find section by title:
  - title: "The Problem"
    content: |
      Updated prose here...
```

### Brief types and filename patterns
| Type | YAML file | Output filename |
|------|-----------|-----------------|
| Numbered brief | `b01.yaml`–`b99.yaml` | `Brief_01_Title.md` |
| Emergency brief | `eb01.yaml` | `Emergency_Brief_Title_v2.md` |
| Executive summary | `es.yaml` | `00_Convergence_Briefs_-_Executive_Summary.md` |
| Introduction | `intro.yaml` | `01_Convergence_Briefs_-_Introduction.md` |
| Supplemental | `supp_*.yaml` | `Title_Slug.md` |

### Brief status values
`STABLE` | `CURRENT` | `NEEDS_UPDATE` | `DRAFT` | `SUPERSEDED`

### Update metadata (version, date)
```yaml
# Top-level fields in any YAML file:
version: "2.0"
date: "2026-03-05"
source: "v1.9 + Session 22 integration"
```

---

## ID Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Stock variable | `SV-NN` | SV-01, SV-18 |
| Flow variable | `FV-NN` | FV-01, FV-24 |
| Threshold variable | `TV-NN` | TV-01, TV-19 |
| Positive optionality | `PO-NN` | PO-01, PO-10 |
| Normalization quality | `NQ-NN` | NQ-01, NQ-10 |
| Session gap | `GNN-NN` | G12-01, G21-05 |
| Legacy gap | `gap-slug` | gap-artesh-loyalty |
| Trap | integer | 1, 14 |
| Observation | integer | 1, 30 |
| Scenario (wartime) | `W{n}` | W1, W5 |
| Scenario (legacy) | `S{n}{letter?}` | S1, S1A |

---

## Schema Validation Rules

Each entity type has a JSON Schema in `schemas/`. Key constraints:

- **Variables:** `id` must match `^(SV|FV|TV|PO|NQ)-\d{2}$`
- **Gaps:** `id` must match `^(G\d{2}-\d{2}|gap-[a-z0-9-]+)$`
- **Gaps:** `priority` must be 1–4 (integer)
- **Gaps:** `status` must be one of: `OPEN`, `PARTIALLY_FILLED`, `FILLED`,
  `DEPRIORITIZED`, `ELEVATED`, `CONFLICT`
- **Content modules:** `module_code` must match a registered code in `modules.yaml`
- **Briefs:** `type` must be one of: `brief`, `emergency_brief`, `executive_summary`,
  `introduction`, `supplemental`
- All entities require fields specified in their schema `required` arrays
- `additionalProperties: false` on all schemas — unknown keys fail validation

---

## Integration Spec → Database Updates

When a Claude session produces an Integration Spec, translate it to database operations:

1. **New variables** → append to `data/variables.yaml`
2. **Updated variables** → find by ID, update changed fields
3. **New gaps** → append to `data/gaps.yaml`
4. **Filled gaps** → update `status` + `session_filled` + `fill_note`
5. **New observations/traps/scenarios** → append to respective files
6. **Version bump** → update `version`, `date`, `source` metadata fields
7. **Validate:**
   ```bash
   python validate.py && python validate_briefs.py
   ```
8. **Build:**
   ```bash
   python build.py && python build_briefs.py
   ```
9. **Commit** (output/ and releases/ are gitignored — do not use `git add -A`):
   ```bash
   git add data/ schemas/ templates/ scripts/ *.py *.md
   git commit -m "Session N: [summary]"
   ```

---

## PDF Release Workflow

After data integration and build:

```bash
python build_pdf.py                    # both tiers → releases/
python build_pdf.py --briefs-only      # Tier 1 only
python build_pdf.py --full-only        # Tier 2 only
python build_pdf.py --date 2026-03-05  # override release date
```

Then create a GitHub Release tagged `v{YYYY-MM-DD}` and attach the PDFs from
`releases/` as release assets. Fill release description from `RELEASE_NOTES_TEMPLATE.md`.

---

## Claude-to-Claude Coordination

Analytical research happens in **Claude Chat** sessions; repository maintenance
happens in **Claude Code** sessions. The two coordinate via `CLAUDE_SESSION_LOG.md`.

### Workflow

1. **Chat** completes an analytical session and appends an Integration Request to
   the log — listing new entities, updated fields, filled gaps, session number, and
   any ambiguities.
2. **Code** reads the log, translates the request into YAML edits, validates, builds,
   and commits. Then appends an Integration Complete entry.
3. **Code** prunes resolved request/confirmation pairs on subsequent sessions.
   Git preserves full history.

### Rules

- Both sides append; neither edits the other's entries.
- Only Code deletes resolved entries.
- Integration requests must reference session numbers and entity IDs, not dump
  large prose blocks into the log.
- When in doubt, the human owner resolves conflicts.

See `CLAUDE_SESSION_LOG.md` for the full protocol and entry format.

---

## Staging Directory Protocol

Chat delivers large content (new briefs, content modules, variable/gap batches)
via the `staging/` directory at the repo root. This directory is gitignored —
it exists only as a transfer mechanism between Chat and Code.

### Layout

```
staging/
└── session_N/              # One directory per analytical session
    ├── b14.yaml            # New brief — full file, copy to data/briefs/
    ├── itb_a13.yaml        # New content module — full file, copy to data/content/
    ├── variables_patch.yaml # Variable updates — merge into data/variables.yaml
    ├── gaps_patch.yaml     # Gap updates — merge into data/gaps.yaml
    └── README.md           # Optional: notes on ambiguities or special handling
```

### Filename Convention

| Suffix | Mode | Action |
|--------|------|--------|
| No `_patch` suffix | **Full file** | Copy directly to target location in `data/` |
| `_patch` suffix | **Field-level merge** | Apply updates to existing YAML by entity ID |

### Patch File Format

Patch files contain a YAML list of updates keyed by entity ID:

```yaml
# variables_patch.yaml — merge into data/variables.yaml
patches:
  - id: SV-01
    fields:
      current_value: "new value"
      trend: "deteriorating"
  - id: FV-12
    fields:
      current_value: "updated"
      confidence: "Low"
```

Code finds each entity by `id` in the target file and updates only the
specified fields. Fields not listed are left unchanged.

### Code Workflow

1. Read `CLAUDE_SESSION_LOG.md` for pending Integration Requests
2. For each request referencing staging files:
   a. Read files from `staging/session_N/`
   b. Full files → copy to `data/` target path
   c. Patch files → merge field updates into existing YAML
   d. Validate: `python validate.py && python validate_briefs.py`
   e. Build: `python build.py && python build_briefs.py`
3. Delete the consumed `staging/session_N/` directory
4. Commit everything atomically:
   ```bash
   git add data/ schemas/ templates/ scripts/ *.py *.md .gitignore
   git commit -m "Session N: [summary from integration request]"
   ```
5. Append an Integration Complete entry to `CLAUDE_SESSION_LOG.md`

### Rules

- Code owns all git operations. Chat never runs `git commit`, `git add`, or `git push`.
- Code deletes staging directories only after successful validation and build.
- If a staging file fails validation, Code appends a Question entry to the log
  describing the failure. Code does not partially integrate — fix or skip the
  entire session's staging batch.
- Chat may also write directly to `CLAUDE_SESSION_LOG.md` (append only).
  Code commits the log along with data changes in the same atomic commit.

---

## Mojibake Handling

All current YAML content files are clean. If mojibake appears in rendered output,
the source is a legacy string in YAML — repair with `ftfy.fix_text()` and update
the YAML source (not the output file).

Common patterns:

| Corrupted | Correct |
|-----------|---------|
| `â€"` | `—` (em dash) |
| `â€"` | `–` (en dash) |
| `Â§` | `§` (section sign) |

**Heredoc note:** For long markdown content in bash, use
`cat > filepath << 'ENDOFFILE'` — preserves special characters reliably.

---

## Migration History (All Complete)

| Phase | Description |
|-------|-------------|
| 0 | Variables, Gaps — pipeline proven |
| 1 | Traps, Observations, Scenarios, Sessions, Modules |
| 2 | 22 ITB/ISA module prose files in `data/content/` |
| 3 | 17 convergence briefs in `data/briefs/` |
| 3e | Testing, cleanup, index wiring |
| PDF | `build_pdf.py` two-tier release builder |

All phases complete. Hand-edited markdown workflow retired.
