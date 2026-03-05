# Claude-to-Claude Session Log

Coordination log between **Claude Chat** (analytical research sessions) and
**Claude Code** (repository maintenance). Both may append entries. Only Claude Code
may delete entries that are fully resolved. Git tracks all history.

---

## Protocol

### Entry format

```
### YYYY-MM-DD — [Source] — [Type]

Body text.
```

- **Source:** `Chat` or `Code`
- **Type:** one of:
  - `Integration Request` — Chat asks Code to commit analytical output to the database
  - `Integration Complete` — Code confirms an integration request has been applied
  - `Question` — either side asks the other for clarification
  - `Note` — informational, no action required
  - `Cleanup` — Code signals that resolved entries above have been pruned

### Rules

1. **Append only** — new entries go at the bottom, above the `<!-- END LOG -->` marker.
2. **Never edit another side's entries** — respond with a new entry instead.
3. **Code owns cleanup** — after an integration is confirmed and verified, Code may
   remove the request + confirmation pair on a subsequent session. Git preserves history.
4. **Keep entries concise** — link to session numbers or entity IDs rather than
   duplicating large blocks of content.
5. **Integration requests must include:**
   - Session number
   - Summary of changes (new entities, updated fields, filled gaps, etc.)
   - Any ambiguities or decisions that need human confirmation

---

## Log

*(No entries yet.)*

<!-- END LOG -->
