# Guide for Analysts

**Using the ITP Framework for Policy, Research, and Reporting**

---

## What This Guide Covers

This guide is for policy professionals, journalists, researchers, and anyone
working on Iran who wants to use this framework's analytical output — without
needing to understand the build pipeline, YAML files, or code.

If you want to understand how the technical machinery works or fork the
repository for your own project, see [Guide for Engineers](GUIDE_ENGINEERS.md).

---

## How the Framework Is Organized

The project produces three layers of analysis, each building on the one below:

**Layer 1: The Iran Transition Baseline (ITB)** is the structural foundation.
It maps how the regime actually works across eight pillars — constitutional
architecture, security apparatus, economics, international alignment, domestic
society, transition dynamics, nuclear program, and information environment.
Twenty-two analytical modules, each with explicit section numbering and
cross-references.

**Layer 2: The Iran Stress Architecture (ISA)** identifies where the system
is vulnerable and where Western analysis consistently breaks. It contains
three entity types:

- **Traps** are circular logic structures that catch policymakers. A trap
  documents its mechanism, its circular structure, what would break the
  circularity, and historical cases where the same pattern has played out.
  Fourteen documented.

- **Observations** are "so-what" findings that emerge from cross-referencing
  ITB modules. Each one states a diagnosis (what is true) and a strategic
  implication (what it means for planning). Thirty logged.

- **Scenarios** model transition and conflict pathways with probability
  ranges, leading indicators, and cross-referenced variables. Twelve modeled.

**Layer 3: Convergence Briefs** translate framework findings into focused,
publication-length analysis. Each brief isolates a specific structural problem
and traces its implications. These are the primary entry point for most
readers — start here and follow cross-references deeper into the framework
when you need the underlying evidence.

Supporting these layers: eighty-six tracked **variables** (structural
conditions, dynamic indicators, trigger thresholds) and fifty-seven registered
**research gaps** (open questions with priority and status tracking).

---

## How to Read Framework Output

### Epistemic Tags

Every analytical claim in the framework carries an inline tag:

| Tag | What It Means | How Much Weight It Bears |
|-----|---------------|------------------------|
| `[Fact — High]` | Directly verifiable, multiple independent sources | Treat as established |
| `[Inference — Med]` | Reasoned from established facts, logic chain stated | Reliable but dependent on premises |
| `[Uncertain — Low]` | Single source, contested, or extrapolated | Use cautiously; may change with new evidence |
| `[Speculation]` | Forward projection, acknowledged hypothesis | Do not cite as a finding |

The tag tells you at a glance whether a specific claim can support the weight
of a policy recommendation or a published assertion. Traditional analytical
products rarely make this visible — you would need to trace the sourcing
appendix to make the same judgment.

**Practical rule:** If you are citing a framework finding in your own work,
cite the tag alongside it. A finding tagged `[Inference — Med]` is an
analytical conclusion with stated reasoning — credible but conditional. A
finding tagged `[Fact — High]` is sourced bedrock. The distinction matters
for your readers as much as for ours.

### Cross-References

Framework documents use a consistent reference format: `MODULE-SECTION`
(e.g., ITB-A10 S3.4, ISA-TRAPS Trap 8). When you encounter a
cross-reference, it points to a specific module and section in the
structured database. In the published output (PDFs and markdown), these
references link to or name the relevant document.

Cross-references are not decorative. They trace the evidence chain — the
claim you are reading rests on analysis developed elsewhere in the
framework, and the reference tells you exactly where to verify or
challenge it.

### Source Hierarchy

The project applies a five-tier source taxonomy:

1. **Regime primary sources** — KHAMENEI.IR, official institutional output,
   seminary publications, IRGC-affiliated media
2. **Human rights monitoring organizations** — HRANA, Amnesty, CHRI
3. **Academic Iran studies** — peer-reviewed research
4. **Diaspora investigative outlets** — with transparent sourcing methodology
5. **Unverified or single-source**

Two points that matter for how you use the output:

First, regime primary sources are not treated as factual reporting. They are
treated as signaling data — what the regime chooses to say, to whom, and when.
When the framework cites KHAMENEI.IR, the analytical signal is the publication
decision, not the content's truth value.

Second, Wikipedia is excluded as a primary or corroborating source for Iran
content. This is a deliberate methodological choice based on documented
state-affiliated manipulation of Iran-related Wikipedia articles.

---

## How to Navigate the Framework

### Starting from a Policy Question

If you have a specific question — *Can a nuclear deal hold? What happens
after Khamenei? Will the IRGC accept a transition?* — the most efficient
path is:

1. **Start with the briefs.** Scan the brief titles for the one closest to
   your question. Each brief is self-contained with its own introduction and
   evidence base.

2. **Follow cross-references into the ITB/ISA.** The brief will cite specific
   modules, observations, and traps. These give you the underlying structural
   analysis.

3. **Check the variables and gaps.** The variable tables show you what the
   project is tracking and at what confidence. The gap registry shows you
   what the project does not know — and therefore where its conclusions are
   most vulnerable.

### Starting from a Research Interest

If you are working on a specific topic — IRGC economics, succession
dynamics, Chinese weapons transfers, the eschatological faction — the ITB
modules are your entry point. Each module covers a defined analytical domain
with section numbering that allows precise citation.

### Starting from Methodological Interest

If you want to evaluate the framework itself — its assumptions, blind spots,
or analytical choices — start with [Methodology](METHODOLOGY.md). It
describes what the project does differently from traditional analytical
approaches and explicitly invites critique.

---

## Using Framework Findings in Your Own Work

### Citation

Framework output is published under CC BY-SA 4.0. You may cite, excerpt,
and build on any finding with attribution. Suggested citation format:

> Iran Transition Project, "[Module or Brief Title]," version [X.X],
> [date], https://github.com/IranTransitionProject/framework

When citing a specific claim, include its epistemic tag. This preserves
the evidence-quality signal for your readers and distinguishes your use
of the framework from uncritical adoption.

### What the Framework Can and Cannot Do for You

**It can** provide a structured analytical baseline — a map of who holds
power, what binds the system, where the stress points are, and what
historical patterns suggest about transition dynamics. If you are writing
analysis, making policy recommendations, or briefing decision-makers, the
framework gives you a cross-referenced evidence base to work from.

**It cannot** replace classified intelligence, human source networks, or
real-time operational data. The project relies entirely on open sources.
Operational military details, internal regime communications, and signals
intelligence are outside its reach. The framework structures and validates
the analytical interpretation — it does not generate the raw intelligence.

**It cannot** tell you what to recommend. The framework is factionally
neutral by design. It maps what must be true regardless of who governs,
not what policy outcome is preferable. Your policy judgment is yours.

### Challenging the Framework

The framework is designed to be challenged, not adopted wholesale. The
most productive challenges target:

- **Confidence bands that seem too high.** Where does the evidence not
  support the stated confidence? Where should `[Inference — Med]` be
  `[Uncertain — Low]`?

- **Missing variables or gaps.** What is the framework not tracking that
  it should be? What open questions are unregistered?

- **Structural blind spots.** What categories of information does the
  framework's architecture systematically exclude? Not individual errors,
  but patterns.

- **Source gaps.** Where does the analysis rest entirely on English-language
  sourcing for a topic that requires Farsi or Arabic sources?

- **Trap or scenario completeness.** Are there circular logic structures
  or transition pathways the framework has not identified?

These are the critiques that improve the framework. Challenges that
substitute a preferred political outcome for analytical neutrality, or
that assert conclusions without sourcing, do not meet the project's
standards — but methodological disagreements always do.

---

## Contributing Without Code

You do not need to touch a YAML file, run a build script, or open a
terminal to contribute to this project. The highest-value analytical
contributions are:

**Persian-language source integration.** The framework's multilingual
mandate is only as strong as the sources it can access. If you read
Farsi and can identify regime primary sources, seminary publications,
or institutional media that bear on framework findings, that is a
high-priority contribution.

**Subject matter review.** Read a module or brief in your area of
expertise. Where is it wrong? Where is it undersourced? Where does the
confidence band not match the evidence? A structured critique —
identifying the specific claim, its current tag, and what evidence
would change it — is more valuable than general feedback.

**Historical case analysis.** The framework uses historical parallels
for transition dynamics (South Africa, Chile, Soviet Union, others).
If you have expertise in a relevant case and can identify where the
parallel holds or breaks, that directly strengthens the scenario
modeling.

**Gap resolution.** The research gap registry is public. If you have
access to information that could fill an open gap — a source, a data
point, a subject matter judgment — submit it through the channels below.

### How to Submit

All of these can be submitted without touching the repository:

- **Public discussion:** [GitHub Discussions](../../discussions)
  (Feedback & Critique category)
- **Private submissions:** [irantransitionproject.org/submit](https://irantransitionproject.org/submit)
- **Email:** [admin@irantransitionproject.org](mailto:admin@irantransitionproject.org)

If your contribution involves structured data (new variables, gap fills,
observation proposals), the project maintainers will handle the YAML
integration. You provide the analysis; the pipeline handles the formatting.

See [Submissions Protocol](SUBMISSIONS.md) for detailed guidance on what
to include with different types of contributions.

---

## A Note on AI-Assisted Analysis

This project uses Claude (Anthropic) as a research assistant. The full
details are in [Methodology](METHODOLOGY.md) and
[Working with LLMs](WORKING_WITH_LLMS.md), but the key points for
analysts evaluating the framework's output:

The AI accelerates research — multilingual source retrieval, structured
data maintenance, draft generation — but it is not a source. Every claim
in the framework requires independent sourcing and epistemic tagging
per the standards described above. AI-generated content that cannot be
sourced is not published.

The instruction files that govern AI behavior are public. If you suspect
the AI-assisted workflow introduces bias, you can read the exact
constraints it operates under and critique them. This is by design.

---

## Questions

- **Analytical:** [GitHub Discussions](../../discussions) or
  [admin@irantransitionproject.org](mailto:admin@irantransitionproject.org)
- **Technical:** See [Guide for Engineers](GUIDE_ENGINEERS.md)
- **Submissions:** See [Submissions Protocol](SUBMISSIONS.md)
