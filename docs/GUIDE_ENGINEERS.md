# Guide for Engineers and Developers

**Using the ITP Framework for AI-Assisted Structured Analysis**

---

## What This Guide Covers

This guide is for software developers, engineers, and technical people who
want to understand how this project works under the hood — and potentially
use the same approach for their own analytical work.

You do not need to be a political scientist or Iran expert. The analytical
methodology is documented in [METHODOLOGY.md](METHODOLOGY.md). This guide
covers the technical machinery.

---

## Architecture in 60 Seconds

```
YAML source files (data/)
    │
    ├── validated against JSON Schemas (schemas/)
    │
    ├── rendered through Jinja2 templates (templates/)
    │
    └── built into Markdown and PDF outputs (pipeline/)
```

Everything is structured data. The YAML files in `data/` are the single
source of truth. The build pipeline renders them deterministically. Hand-edited
markdown was eliminated after compounding consistency errors across sessions.

For the complete technical reference — directory layout, schema constraints,
build commands, common operations — see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## The AI-Assisted Workflow

Two Claude instances divide labor:

| Instance | Role | Instruction File |
|----------|------|-----------------|
| **Claude Chat** | Analytical research — source analysis, framework development, brief drafting | `CLAUDE_CHAT_INSTRUCTIONS.md` |
| **Claude Code** | Repository maintenance — YAML edits, validation, builds, commits | `CLAUDE_CODE_INSTRUCTIONS.md` |

They coordinate via `CLAUDE_SESSION_LOG.md`, an append-only log where Chat
posts integration requests and Code confirms execution. Large content
transfers use a `staging/` directory (gitignored).

The instruction files are the most interesting part for reuse. They encode:
- A modular stakes-based activation system (what analysis depth to apply when)
- Epistemic discipline rules (how to tag uncertainty)
- Source hierarchy and verification standards
- Session management protocols (how to maintain continuity across conversations)
- A structured deliverable format (how sessions produce database updates)

---

## Forking This for Your Own Project

### Step 1: Fork and Strip

```bash
git clone https://github.com/IranTransitionProject/framework.git my-project
cd my-project
rm -rf data/content/* data/briefs/*  # Remove Iran-specific content
# Keep: schemas/, templates/, pipeline/, data/*.yaml (as structural templates)
```

### Step 2: Adapt the Schemas

The JSON Schemas in `schemas/` define what your data looks like. The current
schemas are designed for geopolitical analysis, but the patterns are generic:

- **Variables** — anything you want to track over time with confidence and trend
- **Gaps** — open questions with priority and status tracking
- **Observations** — analytical findings with diagnosis and strategic implication
- **Traps** — circular logic structures that create policy deadlocks
- **Scenarios** — modeled futures with probability ranges

Modify the schemas to fit your domain. The validation pipeline enforces
whatever constraints you define.

### Step 3: Adapt the Instruction Files

The instruction files are designed to be domain-independent at the structural
level. To adapt them:

**CLAUDE_CHAT_INSTRUCTIONS.md** — The core framework (stakes classification,
module system, epistemic tagging, output protocol) works for any analytical
domain. Replace:
- Domain-specific source hierarchies
- Project-specific cross-references
- The Session Deliverable Protocol section (paths, staging conventions)

**CLAUDE_CODE_INSTRUCTIONS.md** — Replace the data operation examples and
schema documentation with your own. The coordination protocol
(session log, staging directory) works as-is.

### Step 4: Link to Your LLM Account

**Claude (Anthropic):**
1. Create a Claude Project at [claude.ai](https://claude.ai)
2. Connect your forked repository to the project (Settings → Project Knowledge → GitHub)
3. Add the project starter instruction (see below)
4. Your instruction files sync automatically from the repo

**Other LLMs:** The instruction files are plain markdown. They can be loaded
as system prompts, uploaded as context documents, or pasted into custom
instructions in any LLM interface. The structured format (numbered modules,
explicit trigger conditions) is designed to be model-agnostic even though
it was developed on Claude.

### Project Starter Instruction

Add this to your LLM project configuration:

> Your operating instructions are maintained in the project Git repository as
> `CLAUDE_CHAT_INSTRUCTIONS.md`. Access them in priority order: (1) If
> filesystem tools are available, read from the local clone. (2) Otherwise,
> use project knowledge search to find them in synced repository files.
> The repo is the single source of truth.

---

## The Build Pipeline

### Quick Start

```bash
pip install pyyaml jsonschema jinja2 ftfy weasyprint markdown

python pipeline/validate.py && python pipeline/validate_briefs.py   # validate all
python pipeline/build.py && python pipeline/build_briefs.py          # build markdown
python pipeline/build_pdf.py                                        # build PDF releases
```

All commands run from the repository root.

### What Each Script Does

| Script | Input | Output |
|--------|-------|--------|
| `pipeline/validate.py` | `data/*.yaml` + `schemas/*.json` | Pass/fail (exit code) |
| `pipeline/validate_briefs.py` | `data/briefs/*.yaml` + `schemas/brief.schema.json` | Pass/fail |
| `pipeline/build.py` | `data/*.yaml` + `templates/*.j2` | `output/*.md` |
| `pipeline/build_briefs.py` | `data/briefs/*.yaml` + `templates/brief*.j2` | `output/*.md` |
| `pipeline/build_pdf.py` | `output/*.md` | `releases/*.pdf` |

The pipeline is intentionally simple — Python, YAML, Jinja2, no framework
dependencies. This is a design choice: analytical projects should not require
learning React or standing up a web server.

---

## Data Patterns Worth Stealing

### Epistemic Tags as Data

Every claim in the YAML content files carries an inline tag like `[Fact -- High]`
or `[Inference -- Med]`. These are rendered as-is in output. This is deliberately
low-tech — no structured metadata on individual claims, just visible inline
markers that a reader can scan.

For a more structured approach, you could extract tags into separate fields
and build dashboards or filters. The project chose inline visibility over
structured queryability.

### The Trap Pattern

The "trap" entity type is novel and potentially useful in other domains.
A trap is a circular dependency that creates a policy deadlock:

```yaml
mechanism: "How the trap operates"
circular_structure: "A requires B → B requires C → C requires A"
resolution_path: "How to break the circularity"
detection_signal: "What to monitor for early warning"
historical_parallels:
  - case: "Country — Event"
    lesson: "What this teaches"
```

This pattern could apply to regulatory deadlocks, organizational change
resistance, technical debt cycles, or any domain where circular dependencies
prevent progress.

### Session-Based Updates

Each analytical session is a numbered event that produces:
- New or updated entities (variables, observations, gaps)
- Version bumps on affected files
- A session log entry documenting what changed

This creates a git-native audit trail. You can trace any claim to the session
that produced it, see what evidence was available at that time, and identify
when conclusions changed and why.

---

## Contributing Technical Improvements

The build pipeline, schemas, and templates are all open for improvement.
High-value technical contributions:

- **Search and query tools** — the YAML data could support a lightweight
  query interface for researchers who want to explore variables, gaps,
  and observations without reading markdown files
- **Visualization** — scenario probability tracking, variable trend charts,
  gap priority heat maps
- **Validation enhancements** — cross-reference integrity checking
  (does every ITB anchor in an observation actually exist in the referenced
  module?)
- **Alternative renderers** — HTML/web output alongside PDF

See [CONTRIBUTING.md](CONTRIBUTING.md) for standards. All contributors
must sign the CLA.

---

## Questions

- **Technical:** Open a GitHub Issue or Discussion
- **General:** [admin@irantransitionproject.org](mailto:admin@irantransitionproject.org)
