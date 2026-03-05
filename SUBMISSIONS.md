# Community Submissions Protocol

**Iran Transition Project**
**Effective:** 2026-03-05
**Status:** DRAFT — pending form implementation

---

## Purpose

Enable anyone — not just formal contributors — to submit source leads, factual
corrections, critiques, and ideas to the project. This protocol defines two intake
channels, consent requirements, triage rules, and processing standards.

Formal contributions (code, analytical content, data) still require the CLA and
pull request process described in `CONTRIBUTING.md`. This protocol covers everything
below that threshold.

---

## Intake Channels

### Channel 1: GitHub Discussions (Public)

**For:** General feedback, critique, methodology questions, ideas, non-sensitive
corrections, public discussion of published briefs.

**Visibility:** Public. Anyone can read submissions and responses.

**Categories:**

| Category | Description |
|----------|-------------|
| Feedback & Critique | Methodological critique, analytical disagreements, framework suggestions |
| Corrections | Factual errors in published briefs or modules (non-sensitive) |
| Ideas | Research directions, case study suggestions, gap identification |
| Questions | Questions about the project, methodology, or analytical conclusions |

**Do not use for:** Source leads that could identify individuals inside Iran,
unpublished documents, or any information the submitter does not want publicly
attributed to them.

### Channel 2: Private Submission Form (Confidential)

**For:** Source leads, sensitive corrections, unpublished documents, information
the submitter wants to share without public attribution.

**Visibility:** Private. Submissions go to the project maintainer only.
Not stored in the public repository.

**URL:** `https://irantransitionproject.org/submit` *(pending implementation)*

**Form fields:**
- Name (optional)
- Email (optional — required if submitter wants follow-up)
- Submission type: Source / Lead | Factual Correction | Sensitive Information | Other
- Content (free text)
- URL or document reference (optional)
- Language of source material (if applicable)
- Consent checkbox (required — see Consent Language below)

**Backend:** Form POSTs to a backend service (Formspree, Netlify Forms, or
equivalent). Submissions route to the project maintainer's email or a private
data store. No submission data is stored in the public GitHub repository.

---

## Consent Language

### GitHub Discussions (public channel)

GitHub's Terms of Service govern public posts. No additional consent required
beyond GitHub's existing terms. The project README notes that discussion content
may inform analytical work.

### Private Submission Form

The following consent text must be accepted (checkbox) before submission:

> **Submission Terms**
>
> By submitting this form, you agree to the following:
>
> 1. You grant the Iran Transition Project a non-exclusive, irrevocable,
>    worldwide right to use the content of this submission in its analytical
>    work, published under CC BY-SA 4.0.
> 2. You represent that this submission does not violate any third-party
>    rights and that you have the authority to share this information.
> 3. If you provide contact information, it will be used only for follow-up
>    questions about this submission and will not be shared publicly or with
>    third parties.
> 4. Anonymous submissions are accepted. If you do not provide contact
>    information, the project cannot follow up with questions.
> 5. The project may choose not to use your submission for any reason.
>    Submission does not guarantee integration into published work.
> 6. If your submission is used, the project may credit you by name only
>    if you explicitly request attribution. Default is no attribution.
>
> **Safety note:** If sharing information that could identify individuals
> at risk, consider whether submission creates danger for them or for you.
> The project takes reasonable precautions with private submissions but
> cannot guarantee security against state-level adversaries. Do not submit
> information that could endanger lives if intercepted.

---

## Triage Protocol

Chat processes submissions at session start (or when directed by the user).

### Triage Categories

| Category | Action | Timeline |
|----------|--------|----------|
| **Source / Lead with URL** | Verify source reliability. Check against gap registry (`data/gaps.yaml`). If relevant, file as research note or fill gap via Integration Request. | Next analytical session |
| **Factual correction** | Check claim against ITB/ISA baseline. If confirmed, flag for integration. If disputed, note the dispute and evidence on both sides. | Next analytical session |
| **Methodological critique** | Evaluate against project methodology. If it identifies a real weakness, flag for framework update. If it reflects a misunderstanding, draft a response (public channel) or note (private channel). | Within 2 sessions |
| **Idea / suggestion** | Log in triage record. Assess relevance to current gaps or research priorities. Defer or integrate. | Best effort |
| **Spam / advocacy / factional content** | Discard. Brief note in triage log. No response unless public channel (then: short redirect to project standards). | Immediate |
| **Sensitive information** | Flag for user review before any processing. Chat does not independently act on sensitive submissions — user decides handling. | Immediate flag, user decides |

### Source Verification Standards

Submitted sources are evaluated using the project's existing 5-tier source taxonomy:

1. Regime primary sources (KHAMENEI.IR tier)
2. Human rights monitoring organizations
3. Academic Iran studies
4. Diaspora investigative outlets with transparent sourcing
5. Unverified / single-source

Submissions that provide sources at tiers 1-3 receive priority processing.
Tier 4-5 sources are logged but flagged for independent verification before
integration into analytical work.

### Triage Log

Each processed submission gets a one-line entry in a triage log:

```
YYYY-MM-DD | [channel] | [type] | [disposition] | [brief note]
```

Example:
```
2026-03-10 | private | source/lead | INTEGRATED → G17-01 | Farsi blog post with CM-302 delivery photos
2026-03-10 | public  | correction  | CONFIRMED → B05 S3  | Date error in Deal Cannot Hold timeline
2026-03-10 | private | sensitive   | FLAGGED FOR USER    | Claims firsthand knowledge of [redacted]
2026-03-10 | public  | feedback    | NOTED               | Suggests adding economic modeling
2026-03-10 | public  | spam        | DISCARDED           | Opposition group recruitment post
```

The triage log is stored privately (not in the public repo). Git-tracked
analytical changes resulting from submissions follow the normal Integration
Request protocol.

---

## Privacy and Safety

### Data Handling

- Private submissions are never committed to the public repository.
- Submitter contact information is never published, shared, or included in
  analytical output.
- If a private submission leads to an analytical finding, the finding is
  attributed to the project's research, not to the submitter, unless the
  submitter explicitly requests attribution.

### Safety Considerations

The project deals with a topic where sources may face physical danger.

- Chat does not process submissions that could identify at-risk individuals
  without explicit user (project owner) review and approval.
- Source descriptions in triage logs and Integration Requests must be
  sufficiently abstract to prevent identification. "Farsi blog post about
  CM-302" is acceptable. The author's name, location, or identifying details
  are not included in any project record.
- If a submission appears to come from someone in immediate danger, the
  project owner is flagged immediately. Chat does not attempt to respond
  or advise on personal safety matters.

---

## Integration with Existing Protocols

Submissions that produce analytical findings follow the standard Chat-to-Code
workflow:

1. Chat triages submission during an analytical session
2. If actionable: Chat writes staging files and/or appends an Integration
   Request to `CLAUDE_SESSION_LOG.md`
3. Code integrates per the normal protocol
4. The submission itself is never referenced in the public commit — only the
   analytical finding it produced

---

## Implementation Checklist

- [ ] Enable GitHub Discussions on the repository (Categories: Feedback & Critique,
      Corrections, Ideas, Questions)
- [ ] Build and deploy private submission form at irantransitionproject.org/submit
- [ ] Configure form backend (email or private data store)
- [ ] Add submission links to README.md, website, and brief footers
- [ ] Create private triage log location (outside public repo)
- [ ] Test end-to-end: submission → triage → integration request → commit
