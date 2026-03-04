# ITP Database: Claude Code Operating Instructions

## Architecture

The Iran Transition Project data is stored as **YAML data files** validated against **JSON Schema** definitions. Markdown reports are **generated artifacts** — never edit them directly.

```
itp-db/
├── data/                    # SOURCE OF TRUTH
│   ├── variables.yaml       # APP-V dashboard (77 entries)
│   ├── gaps.yaml            # APP-G research gaps (35 entries)
│   ├── traps.yaml           # ISA-TRAPS simultaneity traps (12 entries)
│   ├── observations.yaml    # ISA-SCENARIOS observations (21 entries)
│   ├── scenarios.yaml       # ISA-SCENARIOS scenarios (7 entries)
│   ├── sessions.yaml        # Session log (13 entries)
│   ├── modules.yaml         # Module registry (25 entries)
│   ├── index_meta.yaml      # Master index semi-static content
│   ├── content/             # MODULE PROSE (Phase 2, 19 modules)
│   │   ├── itb_a.yaml       # ITB-A: Core Architecture
│   │   ├── itb_b.yaml       # ITB-B: Security & Military
│   │   ├── ...              # (19 total — all ITB + ISA modules)
│   │   └── isa_cases.yaml   # ISA-CASES: Case Studies
│   └── briefs/              # CONVERGENCE BRIEFS (Phase 3, 14 files)
│       ├── b01.yaml         # Brief #1: The Blind Spot in Every Iran Deal
│       ├── b02.yaml         # Brief #2: The Country Inside the Country
│       ├── ...              # (10 numbered briefs)
│       ├── eb01.yaml        # Emergency Brief: Children in the Compound
│       ├── es.yaml          # Executive Summary
│       ├── intro.yaml       # Introduction
│       └── supp_psc.yaml    # Supplemental: Parallel Society Collateral
│
├── schemas/                 # VALIDATION RULES
│   ├── variable.schema.json
│   ├── gap.schema.json
│   ├── trap.schema.json
│   ├── observation.schema.json
│   ├── scenario.schema.json
│   ├── session.schema.json
│   ├── module.schema.json
│   ├── content.schema.json  # Phase 2: module content schema
│   └── brief.schema.json   # Phase 3: brief schema
│
├── templates/               # REPORT TEMPLATES (Jinja2)
│   ├── app_variables.md.j2
│   ├── app_gaps.md.j2
│   ├── isa_traps.md.j2
│   ├── isa_scenarios.md.j2
│   ├── master_index.md.j2   # Renders 00_MASTER_INDEX.md
│   ├── module_content.md.j2 # Generic template for all content modules
│   ├── brief.md.j2          # Phase 3: renders individual briefs
│   ├── brief_changelog.md.j2  # Phase 3: renders changelog
│   └── brief_governance.md.j2 # Phase 3: renders governance framework
│
├── output/                  # GENERATED MARKDOWN (never edit)
│   ├── APPENDIX_VARIABLES.md
│   ├── APPENDIX_GAPS.md
│   ├── ISA_TRAPS.md
│   ├── ISA_SCENARIOS.md
│   ├── 00_MASTER_INDEX.md
│   ├── ITB_*.md             # Phase 2: all content modules
│   ├── ISA_*.md             # Phase 2: ISA content modules
│   ├── Brief_*.md           # Phase 3: numbered briefs
│   ├── Emergency_Brief_*.md # Phase 3: emergency briefs
│   ├── 00_Convergence_*.md  # Phase 3: exec summary
│   ├── 01_Convergence_*.md  # Phase 3: introduction
│   └── FLASH_ANALYSIS_*.md  # Phase 3: supplemental briefs
│
├── scripts/                 # MIGRATION SCRIPTS (one-time use)
│   ├── migrate_variables.py
│   ├── migrate_gaps.py
│   ├── cleanup_variables.py
│   ├── migrate_content.py   # Phase 2: module content migration
│   ├── migrate_b03.py       # Phase 3: single brief migration example
│   └── migrate_all_briefs.py # Phase 3: bulk brief migration
│
├── validate.py              # Schema validation + cross-ref + content + briefs
├── build.py                 # YAML → Markdown renderer (reports + content + briefs)
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
python build.py             # all reports + content + briefs
python build.py variables   # one report
python build.py content     # content modules only
python build.py briefs      # briefs only
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

### Add a new observation
```yaml
# Append to data/observations.yaml entries list:
- id: 22                    # Next sequential integer
  title: "Short Descriptive Title"
  diagnosis: >-
    What is true (analytical finding).
  strategic_implication: >-
    What this means for planning.
  itb_anchors: ["ITB-A10", "ISA-TRAPS Trap 8"]
  scenario_impact:           # Optional: per-scenario effects
    S2: "How this affects Scenario 2"
    S3: "How this affects Scenario 3"
  leading_indicators:        # Optional
    - "What to monitor"
  corrections:               # Optional: added when updating later
    - session: 18
      date: "2026-03-01"
      content: "What changed and why"
  sources: ["Source 1"]      # Optional
  cross_refs: ["Obs 010"]   # Optional
  confidence: "[Inference -- Med]"
  version_added: "v1.6"
  session_added: 18
```

### Update a scenario probability
```yaml
# Find scenario by id, update:
  probability_current: "40-55%"
  # Append to probability_history:
  probability_history:
    # ... existing entries ...
    - version: "v1.6"
      range: "40-55%"
      rationale: "Why the probability changed"
```

### Add a new session
```yaml
# Append to data/sessions.yaml entries list:
- number: 18
  date: "2026-03-01"
  summary: "What was accomplished"
  modules_affected: ["ITB-A12", "ISA-SCENARIOS"]
```

### Add a new module
```yaml
# Append to data/modules.yaml entries list:
- code: "ITB-A13"
  file: "ITB_A13_NEW_MODULE.md"
  version: "1.0"
  lines_approx: "~200"
  description: "What this module covers"
  level: 1
  dependencies: ["ITB-A"]
```

### Add a new content module (Phase 2)
```yaml
# Create data/content/itb_a13.yaml:
module_code: ITB-A13          # Must match modules.yaml code
version: "1.0"
date: "2026-03-01"
source: "Session 19"
dependencies: ["ITB-A"]
referenced_by: []
title: "New Module Title"
pillar: "A"
last_verified: "2026-03-01"
confidence: "Med"
sections:
  - id: "A13.1"
    title: "First Section"
    content: |
      Markdown prose here. Supports bullets, tables, inline tags.
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
Find the section by `id` in the content YAML, edit the `content` block:
```yaml
# In data/content/itb_b.yaml, update section B1 content:
  - id: "B1"
    title: "Nuclear Program Status (Post-Midnight Hammer)"
    content: |
      * Updated content here...
```

### Add a new brief (Phase 3)
```yaml
# Create data/briefs/b11.yaml:
brief_id: B11
number: 11
title: "Brief Title"
subtitle: "Optional Subtitle"
author: "Hooman Mehr"
contact: "hooman@mac.com"
series_link: "https://hmehr.substack.com/p/iran-the-convergence-briefs"
version: "v1.0"
date: "2026-03-03"
date_published: "2026-03-03"
status: DRAFT
type: brief
core_thesis: "Single-sentence thesis statement."
itb_anchors: ["ITB-A", "ITB-B"]
sections:
  - title: "First Section"
    content: |
      Markdown prose here.
  - title: "Second Section"
    content: |
      More prose.
source_summary: "~50 English and Farsi sources"
companion_briefs:
  - number: 1
    title: "The Blind Spot in Every Iran Deal"
    link: "https://hmehr.substack.com/p/the-blind-spot"
author_bio: "Author bio text"
```

### Update a brief section
Find the section by title in the brief YAML, edit the `content` block:
```yaml
# In data/briefs/b01.yaml, update section content:
  - title: "The Problem"
    content: |
      Updated prose here...
```

### Brief types and filename patterns
| Type | YAML filename | Output filename |
|------|--------------|-----------------|
| Numbered brief | `b01.yaml` - `b99.yaml` | `Brief_01_Title.md` |
| Emergency brief | `eb01.yaml` | `Emergency_Brief_Title_v2.md` |
| Executive summary | `es.yaml` | `00_Convergence_Briefs_-_Executive_Summary.md` |
| Introduction | `intro.yaml` | `01_Convergence_Briefs_-_Introduction.md` |
| Supplemental | `supp_*.yaml` | `Title_Slug.md` |

### Brief ID patterns
| Type | Pattern | Example |
|------|---------|---------|
| Numbered | `B01`-`B99` | B01, B10 |
| Emergency | `EB01`+ | EB01 |
| Executive summary | `ES` | ES |
| Introduction | `INTRO` | INTRO |
| Supplemental | `SUPP-*` | SUPP-PSC |

### Brief status values
`STABLE`, `CURRENT`, `NEEDS_UPDATE`, `DRAFT`, `SUPERSEDED`

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

## Future Migration (Phase 2-3)

Phase 0 (complete): Variables + Gaps migrated. Pipeline proven.

Phase 1 (complete): Traps, Observations (21), Scenarios (7), Sessions (13), Modules (25) migrated.
- Prose sections stored as `content` string fields in YAML
- Templates handle rendering
- isa_scenarios.md.j2 template created and tested
- All 190 entries validate against schemas

Phase 2 (in progress): Module prose content (ITB-A through ITB-H, ISA-CORE).
- Each module becomes a YAML file in `data/content/` (e.g., `itb_b.yaml`)
- Schema: `schemas/content.schema.json`
- Template: `templates/module_content.md.j2` (generic, renders any content module)
- Sections[] array with prose blocks (markdown block scalars) + structured metadata
- Section metadata: id, title, level, tags, subsections (recursive)
- Module metadata: module_code, version, date, source, dependencies, referenced_by, pillar, confidence
- Mojibake cleaned during migration (â€" → —, â€" → –, Â§ → §)
- `module_code` must match a registered code in `modules.yaml`
- Build: `python build.py` builds all content modules + all reports
- Build: `python build.py content` builds only content modules
- Validate: `python validate.py` validates content files automatically
- master_index.md.j2 template created, driven by modules.yaml + sessions.yaml + index_meta.yaml
- index_meta.yaml holds semi-static content: governance protocol, dependency map, quick lookup, analytical summary

Completed migrations (19 modules): ITB-A, ITB-A6, ITB-A8, ITB-A9, ITB-A10, ITB-A11, ITB-A12, ITB-B, ITB-C, ITB-D, ITB-D16, ITB-E, ITB-F, ITB-F11, ITB-F12, ITB-G, ITB-H, ISA-CORE, ISA-CASES
Phase 2 COMPLETE. All module prose content migrated to YAML.

Phase 3 (complete): Convergence Briefs migrated to YAML.
- 14 brief YAML files in `data/briefs/` (10 numbered + 1 emergency + 1 exec summary + 1 intro + 1 supplemental)
- Schema: `schemas/brief.schema.json`
- Template: `templates/brief.md.j2` (renders all brief types)
- Additional templates: `brief_changelog.md.j2`, `brief_governance.md.j2`
- Build: `python build.py` builds all briefs + all content + all reports
- Build: `python build.py briefs` builds only briefs
- Validate: `python validate.py` validates briefs automatically
- Brief types: brief, emergency_brief, executive_summary, introduction, supplemental
- All types route through `brief.md.j2` with conditional rendering
- Separate Jinja2 environment for briefs (trim_blocks=False for whitespace fidelity)
- 2,593 total YAML lines across all briefs
Phase 3 COMPLETE. All briefs migrated and integrated into unified pipeline.

Phase 3e (pending): Testing + cleanup.
- Create `index_meta.yaml` with static governance content for Parts 2/3/6/7/8
- Final packaging

## Mojibake Handling

The original markdown files contain UTF-8 mojibake (double-encoded characters). The migration scripts include cleanup functions, but some artifacts may remain. When found:

1. Fix in the YAML source data
2. Do NOT fix in output/*.md (it will be overwritten)
3. Common patterns:
   - `â€"` → `—` (em-dash)
   - `â€"` → `–` (en-dash)
   - `Â§` → `§` (section sign)
