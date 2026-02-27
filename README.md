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

For the full project rationale, see [README_PROJECT.md](README_PROJECT.md).

---

## Repository Structure

```
/
├── schema/              # JSON Schema definitions for all data structures
├── src/                 # YAML source-of-truth files (validated against schema)
│   ├── baseline/        # Iran Transition Baseline (ITB) modules
│   ├── stress/          # Iran Stress Architecture (ISA) modules
│   ├── briefs/          # Policy brief source data
│   └── scenarios/       # Scenario and variable definitions
├── templates/           # Jinja2 templates for artifact generation
│   ├── markdown/
│   ├── html/
│   └── pdf/
├── build/               # Python build scripts
│   ├── build.py         # Main build entry point
│   ├── validate.py      # Schema validation runner
│   └── render.py        # Template rendering engine
├── dist/                # Generated artifacts (do not edit directly)
│   ├── markdown/
│   ├── html/
│   └── pdf/
├── agents/              # Claude Code agent configuration files
├── docs/                # Project documentation
├── LICENSE
├── GOVERNANCE.md
├── CONTRIBUTING.md
├── README.md            # This file
└── README_PROJECT.md    # Full project rationale and background
```

---

## Build System

The project uses a YAML-first architecture. All analytical content lives in
validated YAML source files. Markdown, HTML, and PDF outputs are generated
artifacts — never edited directly.

```bash
# Install dependencies
pip install -r requirements.txt

# Validate all source files against schema
python build/validate.py

# Build all artifacts
python build/build.py

# Build specific output format
python build/build.py --format pdf
python build/build.py --format markdown
```

Requires Python 3.10+.

---

## Current Release

| Module | Version | Status |
|--------|---------|--------|
| Iran Transition Baseline (ITB) | 2.3 | Active |
| Iran Stress Architecture (ISA) | 1.0 | Active |
| Policy Briefs | 5 published | Active |

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
