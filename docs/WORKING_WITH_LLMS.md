# Working with LLMs Effectively

**Iran Transition Project**

---

## Overview

This project uses Claude (Anthropic) as a research and maintenance assistant.
This document describes what LLMs do well, where they fail, and how the project
mitigates those failures. It is written for anyone using LLM tools for analytical
work — technical background not required.

---

## What LLMs Do Well

- **Synthesis across large document sets.** Given a structured knowledge base
  (like this one), an LLM can traverse many entities simultaneously and identify
  patterns that would take hours to surface manually.

- **Structured output generation.** LLMs excel at producing consistently
  formatted output — YAML entries, markdown reports, table summaries — when
  given clear schemas and examples.

- **Rapid drafting.** First drafts of analytical prose, policy summaries, and
  framework documentation can be produced in seconds. The human role shifts to
  editing and verification rather than blank-page writing.

- **Multilingual research.** LLMs can read and reason across Farsi, Arabic,
  and English sources simultaneously — a meaningful advantage for a project
  where critical primary sources are not in English.

- **Consistency enforcement.** With detailed instructions (see
  [CLAUDE_CHAT_INSTRUCTIONS.md](CLAUDE_CHAT_INSTRUCTIONS.md) and
  [CLAUDE_CODE_INSTRUCTIONS.md](CLAUDE_CODE_INSTRUCTIONS.md)), an LLM can
  apply analytical standards consistently across hundreds of entities.

---

## Where LLMs Fail — and How This Project Responds

### 1. Knowledge Cutoff

**The problem:** LLMs are trained on data up to a fixed date. Events after the
cutoff are unknown. This is the most operationally significant limitation for
Iran analysis — a region where the structural picture can shift rapidly.

**This project's response:**
- All time-sensitive analytical claims are explicitly date-stamped.
- Web search tools are required for any claim about events after the model's
  training cutoff.
- Human verification is mandatory for all current-state assertions.
- Standing rule: LLM "knowledge" about Iran after the model's training cutoff
  is treated as hypothesis, not fact, until independently sourced.

---

### 2. Tunnel Vision / Confirmation Bias

**The problem:** LLMs tend to pursue the first analytical frame they encounter
rather than questioning it. Once a framing is established, contradictory
evidence is underweighted.

**This project's response:**
- **Module 8 (Domain Scan):** Forces cross-domain checks across all ITB pillars
  before conclusions are drawn.
- **Module 2 (Truth Engine):** Sophisticated Actor Default — assumes the regime
  is acting rationally within its own logic, not performing for Western audiences.
- **Adversarial mode:** At HIGH stakes, the LLM is explicitly
  instructed to argue against its own previous conclusions.
- **Established-prior reconciliation:** Any new analytical claim must be
  explicitly reconciled with existing ITB/ISA entries, not treated in isolation.

---

### 3. Hallucination

**The problem:** LLMs can generate plausible-sounding but false claims,
especially for niche topics with sparse training data. Iran's internal
institutional architecture is exactly this kind of domain.

**This project's response:**
- **Epistemic tagging requirement:** Every analytical claim must be tagged
  Fact / Inference / Uncertain / Speculation with explicit confidence bands.
  This makes the LLM's uncertainty visible rather than hidden.
- **Source verification mandate:** Any Fact-tagged claim requires a citable
  source. LLM recall alone is never sufficient for Fact classification.
- **Factional neutrality test:** Claims that depend on a preferred political
  outcome are structurally suspect — this filters a significant class of
  motivated reasoning.

---

### 4. False Balance

**The problem:** LLMs default to presenting "both sides" even when one side
is factually wrong. This is sycophancy toward perceived neutrality rather than
accuracy.

**This project's response:**
- **No False Balance rule (Module 2):** Explicit instruction to call
  asymmetric situations asymmetric. If the evidence strongly supports one
  conclusion, the LLM is instructed to say so, not to manufacture a
  "counterpoint" for presentational balance.

---

### 5. Sycophancy

**The problem:** LLMs tend to agree with the user's framing rather than push
back on errors. In analytical work, this produces output that validates
assumptions rather than tests them.

**This project's response:**
- **ADVISOR + ADVERSARIAL modes:** The analytical instruction set includes
  explicit modes where the LLM is required to challenge premises and argue
  the strongest countercase.
- **Truth correction rule:** The LLM is instructed to correct factual errors
  in user prompts, not accommodate them.

---

### 6. Context Window Decay

**The problem:** In long sessions, LLMs lose attention to instructions given
earlier in the conversation. Important constraints established at session start
may be silently violated by session end.

**This project's response:**
- **Long-Session Instruction Decay rule:** Explicit instruction to re-read and
  re-apply core epistemic standards periodically within long sessions.
- **Session compaction protocol:** When context limits approach, the
  conversation is compacted — prior turns are compressed into a structured
  summary while preserving decisions, findings, and key context. The full
  transcript remains available for detail recovery.
- **Session starters:** Each new session begins by reading a session starter
  document that captures prior findings, rather than reconstructing context
  from memory.
- **Chat-to-Code coordination:** Session outputs are delivered as structured
  Integration Requests via a session log, not as prose summaries. This
  forces the LLM to produce concrete, verifiable deliverables rather than
  vague recaps.

---

### 7. AI-Generated Content Contamination

**The problem:** AI-generated text increasingly appears in search results,
social media, and secondary sources. An LLM reading this material and treating
it as evidence creates a circular reasoning problem.

**This project's response:**
- AI-generated text from other systems is treated as hypothesis input only,
  never as independent evidence.
- Source taxonomy (Tier 1-5) excludes AI-generated content from corroborating
  positions.
- Wikipedia is excluded as a primary or corroborating source for Iran content —
  partly for the same reason: it is too easily contaminated by partisan edits
  and AI-assisted content.

---

## Practical Techniques

These are the practices that have produced the best results in this project's
analytical sessions:

**Use structured prompts with explicit instructions.** Vague prompts produce
vague output. The more precisely the analytical task is specified — including
what epistemic tags to use, what cross-references to check, what adversarial
arguments to consider — the more useful the output.

**Verify time-sensitive claims with search.** For any claim about current
Iranian political conditions, use a web search tool rather than relying on
training data. Treat the LLM's initial response as a hypothesis to be verified,
not a conclusion.

**Force the model to show its sources.** Ask explicitly: "What is this based
on? What would change this conclusion?" Unprompted, LLMs often state conclusions
without flagging the evidentiary basis.

**Use epistemic tags to make uncertainty visible.** Asking the LLM to tag every
claim forces it to reason about confidence levels rather than presenting all
output at the same confidence level.

**Break complex analysis into focused sessions.** A session focused on a single
ITB module produces more reliable output than a session ranging across the entire
framework. Smaller scope = less context decay = more consistent application of
standards.

**Maintain session starters for continuity.** Fresh sessions with a good
session starter outperform degraded long sessions. The project's compaction
and session starter protocol exists for this reason. Use it.

**Know when to restart.** If you notice the LLM is contradicting earlier
conclusions without explanation, ignoring epistemic tags, or producing
suspiciously confident claims in a niche domain, restart the session. Degraded
context is a real and observable phenomenon.

---

## Red Flags: When Not to Trust the Output

These patterns indicate the LLM is operating outside its competence or has
accumulated session degradation:

- **Confident claims about specific events after 2024** with no search
  evidence cited
- **Claims that depend on internal Iranian political motivations** stated as
  Fact rather than Inference
- **Round numbers and neat patterns** in data (exact percentages, perfectly
  symmetrical timelines) — real political data is messy
- **Failure to acknowledge uncertainty** on genuinely contested questions
  (e.g., succession planning, IRGC internal politics)
- **Agreement with a framing change** in your prompt without noting the shift
- **Disappearance of epistemic tags** in output from a session that was
  previously tagging correctly

When you see these, treat the output as draft material requiring independent
verification rather than analysis ready for publication.

---

## Project-Specific Notes

The ITP analytical framework was built to counteract specific LLM tendencies.
When Chat-side sessions produce output that seems to violate these principles,
check the session log — the issue may have been identified and corrected in a
prior session, or it may warrant a new analytical gap entry.

For questions about how the AI coordination protocol works technically, see
[GUIDE_ENGINEERS.md](GUIDE_ENGINEERS.md).
For the analytical methodology this LLM workflow supports, see
[METHODOLOGY.md](METHODOLOGY.md).
