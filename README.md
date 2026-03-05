# Iran Transition Project

**Independent analytical framework for Iranian regime architecture and transition dynamics.**

🌐 [irantransitionproject.org](https://irantransitionproject.org)

📧 [admin@irantransitionproject.org](mailto:admin@irantransitionproject.org)

📄 Licensed under [CC BY-SA 4.0](LICENSE) · [Governance](GOVERNANCE.md) · [Contributing](CONTRIBUTING.md)

---

## What This Is

The Iran Transition Project is an open, independent analytical framework examining
how power actually operates inside the Iranian regime, where structural
vulnerabilities exist, and what conditions a viable transition would require.

This is not advocacy for any faction, opposition group, or foreign policy position.
The guiding question throughout is: *what must be true for a transition to succeed,
regardless of who governs?*

For database design and build pipeline details, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Repository Structure

```
/
├── data/                        # YAML source-of-truth files
│   ├── content/                 # ITB/ISA module prose (22 files)
│   ├── briefs/                  # Convergence brief content (17 files)
│   └── *.yaml                   # Variables, gaps, traps, observations, scenarios, sessions
├── schemas/                     # JSON Schema definitions (9 schemas)
├── templates/                   # Jinja2 rendering templates
├── scripts/                     # One-time migration utilities
├── .github/workflows/           # CI configuration
├── build.py                     # Entity reports + content module builder
├── build_briefs.py              # Convergence brief builder
├── build_pdf.py                 # PDF release bundle builder
├── validate.py                  # Schema validation (entities + content)
├── validate_briefs.py           # Schema validation (briefs)
├── ARCHITECTURE.md              # Database design and pipeline documentation
├── CLAUDE_CHAT_INSTRUCTIONS.md  # Operating instructions for Claude Chat (analytical sessions)
├── CLAUDE_CODE_INSTRUCTIONS.md  # Operating instructions for Claude Code (repo maintenance)
├── CLAUDE_SESSION_LOG.md        # Claude-to-Claude coordination log
├── CONTRIBUTING.md
├── GOVERNANCE.md
└── LICENSE
```

---

## Quick Start

```bash
pip install pyyaml jsonschema jinja2 ftfy weasyprint markdown

python validate.py && python validate_briefs.py   # validate
python build.py && python build_briefs.py          # build markdown
python build_pdf.py                                # build PDF releases
```

---

## Releases

PDF bundles are published as [GitHub Releases](../../releases). Each release includes:

| File | Contents | Audience |
|------|----------|----------|
| `ITP-Briefs-v{date}.pdf` | All policy briefs + reference appendix | General / policy |
| `ITP-Reference-v{date}.pdf` | Briefs + full ITB/ISA analytical library | Researchers |

---

## Current State

| Component | Coverage | Status |
|-----------|----------|--------|
| Iran Transition Baseline (ITB) | 8 pillars, 22 modules | Active |
| Iran Stress Architecture (ISA) | Traps, observations, scenarios | Active |
| Policy briefs | 13 published + supplementals | Active |
| Analytical variables | 86 tracked | Active |
| Research gaps | 57 registered (49 open) | Active |

---

## AI-Assisted Research

This project uses Claude (Anthropic) as a research assistant across two interfaces:

- **Claude Chat** conducts analytical sessions — source research, factional analysis,
  framework development, brief drafting. Operating protocol:
  [`CLAUDE_CHAT_INSTRUCTIONS.md`](CLAUDE_CHAT_INSTRUCTIONS.md).
- **Claude Code** maintains the repository — YAML edits, schema validation, builds,
  commits. Operating protocol:
  [`CLAUDE_CODE_INSTRUCTIONS.md`](CLAUDE_CODE_INSTRUCTIONS.md).

The two coordinate via [`CLAUDE_SESSION_LOG.md`](CLAUDE_SESSION_LOG.md), a structured
append-only log where Chat posts integration requests and Code confirms execution.

**Why this is public:** Analytical transparency requires disclosing methods.
AI assistance is a tool, not a source — all claims still require sourcing,
epistemic tagging, and factional neutrality per the project's analytical standards.
The instruction files document exactly what the AI is told to do and what constraints
it operates under.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributors must sign the CLA.

Highest-priority needs: Persian-language source integration, subject matter
review, and methodological critique.

---

## License

[CC BY-SA 4.0](LICENSE) — open for reuse and adaptation with attribution,
derivative works must remain open under the same terms.

Alternative licensing available for policy institutions with copyleft
constraints — contact admin@irantransitionproject.org.
