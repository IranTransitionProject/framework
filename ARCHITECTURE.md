# Iran Transition Project — Database Architecture

Technical reference for the ITP structured database and build pipeline.
For orientation and quickstart, see [README.md](README.md).
For operational session instructions, see [CLAUDE_CODE_INSTRUCTIONS.md](CLAUDE_CODE_INSTRUCTIONS.md).
For project governance and licensing, see [GOVERNANCE.md](GOVERNANCE.md).

---

## Design Philosophy

The original project accumulated 20+ markdown files edited manually across LLM sessions.
This produced compounding errors: line number drift, inconsistent formatting, broken
cross-references, and no schema validation.

The database architecture establishes a single rule: **YAML is the source of truth.
Markdown and PDF are generated artifacts, never hand-edited.**

Every entity — variable, gap, trap, observation, scenario, module, brief — lives in a
validated YAML file. The build pipeline renders these deterministically to markdown and PDF.
Sessions that previously produced patch instructions now produce YAML edits.

---

## Pipeline Overview

```
data/*.yaml            (structured entity data)
data/content/*.yaml    (ITB/ISA module prose)
data/briefs/*.yaml     (convergence brief content)
        │
        ├─── validate.py          schema validation for entity + content files
        ├─── validate_briefs.py   schema validation for brief files
        │
        ├─── build.py             entity reports + content modules → output/
        ├─── build_briefs.py      convergence briefs → output/
        │
        └─── build_pdf.py         output/ → releases/*.pdf → GitHub Release
```

`output/` and `releases/` are gitignored. Distributed content reaches readers only
via GitHub Releases as attached PDF assets.

---

## Data Directory Structure

```
data/
├── variables.yaml       # 86 analytical variables (SV, FV, TV, PO, NQ types)
├── gaps.yaml            # 57 research gaps by priority and status
├── traps.yaml           # 14 analytical traps with session extensions
├── observations.yaml    # 30 observations with status tracking
├── scenarios.yaml       # 12 scenarios (wartime W1-W5 + legacy)
├── sessions.yaml        # 20 session log entries (sessions 1-21)
├── modules.yaml         # Module registry (code, file, version, level)
├── index_meta.yaml      # Static content for master index template
├── content/             # ITB/ISA module prose (22 files)
│   ├── itb_a.yaml
│   ├── itb_a6.yaml
│   ├── itb_b.yaml
│   └── ... (one file per module)
└── briefs/              # Convergence brief content (17 files)
    ├── b01.yaml
    ├── b02.yaml
    └── ... (one file per brief)
```

---

## Schema Conventions

All schemas are JSON Schema Draft-07 in `schemas/`. `additionalProperties: false`
is enforced on every schema — unknown keys fail validation, preventing silent data drift.

### Entity ID Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Stock variable | `SV-NN` | `SV-01`, `SV-18` |
| Flow variable | `FV-NN` | `FV-01`, `FV-24` |
| Threshold variable | `TV-NN` | `TV-01`, `TV-19` |
| Positive optionality | `PO-NN` | `PO-01`, `PO-10` |
| Normalization quality | `NQ-NN` | `NQ-01`, `NQ-10` |
| Session gap | `GNN-NN` | `G12-01`, `G20-05` |
| Legacy gap | `gap-slug` | `gap-artesh-loyalty` |
| Trap | integer | `1`, `14` |
| Observation | integer | `1`, `30` |
| Scenario | `W{n}` or `S{n}` | `W1`, `S1A` |

### Key Schema Constraints

- **Variables:** `id` must match `^(SV|FV|TV|PO|NQ)-\d{2}$`
- **Gaps:** `priority` is integer 1-4; `status` must be one of
  `OPEN | PARTIALLY_FILLED | FILLED | DEPRIORITIZED | ELEVATED | CONFLICT`
- **Traps:** support an `extensions` array for addenda across sessions
- **Content modules:** `module_code` must match a registered code in `modules.yaml`
- **Briefs:** `type` must be one of
  `brief | emergency_brief | executive_summary | introduction | supplemental`

---

## Data File Formats

### Structured Entity Files (`data/*.yaml`)

Each file has a top-level metadata block followed by an `entries` array:

```yaml
version: "1.8"
date: "2026-03-05"
source: "v1.7 + Session 21 integration"
summary:
  total: 86
  # type-specific summary fields
entries:
  - id: SV-01
    name: "..."
    # entity fields per schema
```

`build.py` separates metadata (via `load_metadata()`) from entries (via `load_entries()`)
and passes both to templates.

### Module Prose Files (`data/content/*.yaml`)

One YAML file per module. Sections are a recursive array supporting arbitrary nesting:

```yaml
module_code: "ITB-B"
version: "2.2"
date: "2026-02-28"
title: "Security & Military Architecture"
pillar: "B"
dependencies: ["ITB-A"]
referenced_by: ["ISA-CORE", "ISA-TRAPS"]
sections:
  - id: "B1"
    title: "IRGC Institutional Architecture"
    level: 2
    content: |
      Markdown prose...
    subsections:
      - id: "B1.1"
        title: "..."
        level: 3
        content: |
          ...
```

`module_code` must match a registered code in `modules.yaml`. The `module_content.md.j2`
template renders any content module via recursive section traversal.

### Brief Files (`data/briefs/*.yaml`)

One YAML file per brief. Key fields: `brief_id`, `type`, `number`, `title`, `subtitle`,
`date_published`, `version`, `summary`, `sections[]`, `key_findings[]`, `references[]`.
The `brief.md.j2` template handles all five `type` values via conditional blocks.

---

## Build Scripts

### `validate.py` and `validate_briefs.py`

`validate.py` validates all entity and content files. `validate_briefs.py` validates
brief files. Both return non-zero exit codes on failure. Run both before any commit.

`build.py --validate` invokes `validate.py` as a subprocess before building.

### `build.py`

Renders entity reports and content modules. Uses a single Jinja2 environment
(`trim_blocks=True`, `lstrip_blocks=True`).

| CLI argument | Output file |
|---|---|
| *(none)* | All targets below |
| `variables` | `output/APPENDIX_VARIABLES.md` |
| `gaps` | `output/APPENDIX_GAPS.md` |
| `traps` | `output/ISA_TRAPS.md` |
| `scenarios` | `output/ISA_SCENARIOS.md` |
| `index` | `output/00_MASTER_INDEX.md` |
| `content` | All 22 content module files |
| `--validate` | Runs validate.py first, aborts on failure |

### `build_briefs.py`

Renders convergence briefs. Uses a separate Jinja2 environment
(`trim_blocks=False`, `lstrip_blocks=False`) to preserve whitespace fidelity in
prose-heavy content.

Output filename is derived deterministically from brief `type` and `number`:

| Brief type | Output filename |
|---|---|
| `executive_summary` | `00_Convergence_Briefs_-_Executive_Summary.md` |
| `introduction` | `01_Convergence_Briefs_-_Introduction.md` |
| Numbered brief | `Brief_NN_{Title_Slug}.md` |
| `emergency_brief` | `Emergency_Brief_{Title_Slug}_v2.md` |
| `supplemental` | `{Title_Slug}.md` |

### `build_pdf.py`

Runs after `build.py` and `build_briefs.py`. Reads from `output/`, renders to
`releases/`. Two output tiers:

**Tier 1 — `ITP-Briefs-v{date}.pdf`**
Exec summary → Introduction → Briefs 01-13 → Emergency brief → 4-table reference
appendix (variables, gaps, traps, observations). Clickable TOC. Public audience.

**Tier 2 — `ITP-Reference-v{date}.pdf`**
All Tier 1 content + all 22 ITB/ISA content modules. Two-part TOC. Research audience.

PDF rendering stack: Python `markdown` → HTML with embedded CSS → `weasyprint` → PDF.
A4, Georgia serif, running page numbers. Brief assembly order controlled by
`BRIEF_ORDER_PATTERNS` regex list.

CLI options:

```bash
python build_pdf.py                    # both tiers
python build_pdf.py --briefs-only      # Tier 1 only
python build_pdf.py --full-only        # Tier 2 only
python build_pdf.py --date 2026-03-04  # override release date
```

---

## Release Workflow

```bash
# 1. Edit YAML source files in data/
# 2. Validate
python validate.py && python validate_briefs.py

# 3. Build markdown
python build.py && python build_briefs.py

# 4. Build PDFs
python build_pdf.py

# 5. Commit source changes only (output/ and releases/ are gitignored)
git add data/ schemas/ templates/ scripts/ *.py *.md
git commit -m "Session N: [summary]"

# 6. Tag and push
git tag v2026-03-05
git push origin main --tags

# 7. Create GitHub Release tagged v{YYYY-MM-DD}
#    Body: fill from RELEASE_NOTES_TEMPLATE.md
#    Assets: releases/ITP-Briefs-v{date}.pdf
#            releases/ITP-Reference-v{date}.pdf
```

---

## Mojibake Handling

The original markdown contained double-encoded UTF-8 from multi-tool copy-paste.
Known corruptions and their correct forms:

| Corrupted | Correct | Character |
|-----------|---------|-----------|
| `â€"` | `—` | em dash |
| `â€"` | `–` | en dash |
| `Â§` | `§` | section sign |
| `â€˜` | `'` | left single quote |
| `â€™` | `'` | right single quote |

Migration scripts used `ftfy` for automated repair. All current YAML content files
are clean. If mojibake appears in rendered output, the source is an un-migrated
legacy string — repair with `ftfy.fix_text()`.

**Heredoc reliability note:** For long markdown passed through bash, use heredoc syntax
(`cat > filepath << 'ENDOFFILE'`) — it preserves em-dashes and special characters
reliably. Avoid echo-based approaches for multi-line content.

---

## Migration History

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | Complete | Variables, Gaps — build pipeline proven |
| 1 | Complete | Traps, Observations, Scenarios, Sessions, Modules |
| 2 | Complete | 22 ITB/ISA module prose files in `data/content/` |
| 3 | Complete | 17 convergence briefs in `data/briefs/` |
| 3e | Complete | Testing, cleanup, index wiring |
| PDF | Complete | `build_pdf.py` two-tier release builder |

Hand-edited markdown workflow is retired. All updates go through YAML → validate → build.

---

## Dependencies

```bash
pip install pyyaml jsonschema jinja2 ftfy weasyprint markdown
```

| Package | Purpose |
|---------|---------|
| `pyyaml` | YAML parsing |
| `jsonschema` | Schema validation |
| `jinja2` | Template rendering |
| `ftfy` | Mojibake repair (migration scripts only) |
| `weasyprint` | HTML → PDF (`build_pdf.py`) |
| `markdown` | Markdown → HTML (`build_pdf.py`) |
