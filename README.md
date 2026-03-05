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
├── CLAUDE_CODE_INSTRUCTIONS.md  # Operating manual for AI-assisted sessions
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
