# Iran Transition Project

**Independent analytical framework for Iranian regime architecture and transition dynamics.**

🌐 [irantransitionproject.org](https://irantransitionproject.org)
📧 [admin@irantransitionproject.org](mailto:admin@irantransitionproject.org)
📄 Licensed under [CC BY-SA 4.0](LICENSE) · [Governance](GOVERNANCE.md) · [Contributing](CONTRIBUTING.md)

---

## Why This Exists

In January 2026, the Iranian regime killed and imprisoned thousands of its own people.
That event — and what preceded it over decades — is not in serious dispute. What *is*
disputed, often passionately among Iranians themselves, is what comes next.

Many Iranians who are horrified by the regime are simultaneously terrified of change.
They have watched Iraq disintegrate. They watched Syria burn. They look at Libya. And
they conclude, not irrationally, that the known catastrophe may be safer than an
unknown one. That fear is real. It deserves a serious answer — not dismissal.

This project is that answer, or an attempt at one.

The reason a successful transition feels unimaginable to so many people is largely
because no serious, impartial, publicly available roadmap exists. That gap is not just
an academic problem — it is itself a political force that reinforces paralysis, feeds
regime propaganda, and may ultimately doom the Iranian people to exactly the outcome
everyone fears.

If we can fill that gap, even partially, we change what is imaginable. And what is
imaginable shapes what is possible.

---

## What This Project Is

An open, independent analytical framework examining:

- **Regime architecture** — how power actually flows, who controls what, where
  structural vulnerabilities exist
- **Transition dynamics** — what conditions, sequences, and institutions a successful
  transition would require
- **Failure modes** — the specific mechanisms that turned Iraq, Syria, and Libya into
  catastrophes, and whether they apply to Iran

The framework is organized into modular research documents covering security, economy,
society, ideology, territorial integrity, international positioning, diaspora dynamics,
and information environment — cross-referenced, version-controlled, and maintained as
a living analytical system.

---

## What This Project Is Not

**This is not advocacy for any specific political faction, opposition group, or
foreign policy position.**

It does not endorse regime change by any particular means. It does not align with any
diaspora organization, political party, or government. It does not take positions on
sanctions, military options, or diplomatic strategy — except to analyze their structural
consequences as honestly as possible.

The guiding discipline throughout is a single question: *What must be true for a
transition to succeed, regardless of who governs?*

---

## Repository Structure

This repository is the **structured data layer** of the Iran Transition Project.
Analytical content lives in validated YAML source files. Markdown outputs are
generated artifacts — never edited directly.

```
├── data/           # YAML source of truth (variables, gaps, traps, scenarios)
├── schemas/        # JSON Schema validation rules
├── templates/      # Jinja2 rendering templates
├── scripts/        # Migration and utility scripts
├── output/         # Generated markdown (do not edit)
├── validate.py     # Schema validation runner
└── build.py        # Artifact build system
```

For build instructions, dependency requirements, and data architecture details,
see [ARCHITECTURE.md](ARCHITECTURE.md).

For Claude Code agent operating instructions, see
[CLAUDE_CODE_INSTRUCTIONS.md](CLAUDE_CODE_INSTRUCTIONS.md).

---

## Current Status

| Component | Status | Entries |
|-----------|--------|---------|
| Variables (APP-V) | ✅ Complete | 77 |
| Research Gaps (APP-G) | ✅ Complete | 35 |
| Simultaneity Traps (ISA) | ✅ Complete | 12 |
| Observations | 🔄 Pending migration | — |
| Scenarios | 🔄 Pending migration | — |
| Module prose (ITB-A through ITB-H) | 🔄 Pending migration | — |
| Policy Briefs | 🔄 Pending migration | 5 published |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributors must sign the CLA.

Highest-priority needs:
- Persian-language source integration and translation
- Subject matter review (political science, security studies, economics, law)
- Methodological critique — where the framework is wrong, say so explicitly

---

## Why I Built This

I am an Iranian-American. I am not a professional academic, a policy professional,
or an intelligence analyst. I am someone who looked at what was happening in January
2026, looked for serious, impartial work on what a viable transition might actually
require, and found a gap where that work should have been.

So I started building it.

I believe that a successful transition in Iran — one that produces stability,
accountability, and genuine self-determination for the Iranian people — would be
transformative not just for Iran but for the entire region. The Iranian people's
success is not a sectarian or national interest. It is a regional and human one.

---

## License

[CC BY-SA 4.0](LICENSE) — open for reuse and adaptation with attribution.
Derivative works must remain open under the same terms.

Alternative licensing available for policy institutions with copyleft constraints.
Contact: admin@irantransitionproject.org

---

*Independent research. No institutional affiliation. No factional alignment.*
