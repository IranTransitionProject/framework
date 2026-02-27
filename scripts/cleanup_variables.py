#!/usr/bin/env python3
"""Clean up the migrated variables YAML."""
import yaml
from pathlib import Path

p = Path("/home/claude/itp-db/data/variables.yaml")
with open(p, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

# Clean bold markers from insight field
for entry in data["entries"]:
    if "insight" in entry and entry["insight"]:
        entry["insight"] = entry["insight"].replace("**", "")

# Replace the single concatenated monitoring note with proper list
data["monitoring_notes"] = [
    "Variables require weekly recheck on flow and threshold tables. Stock variables recheck monthly or on significant event.",
    "v1.2 NOTE (still active): Given active mourning cycle, Hormuz exercise tempo, and campaign-ready US force posture, flow and threshold variables should be rechecked every 3-5 days until situation stabilizes or transitions to a new phase.",
    "v1.3 NOTE: Paydari trajectory and Ghalibaf timeline variables are election-cycle dependent (2028); monitor Guardian Council candidate approval patterns in 2027 as leading indicator. Judicial moratorium threshold is instantaneous upon any transition event -- no warning lag.",
    "v1.5 NOTE (CRITICAL): Trump deadline variables, Iran proposal delivery, Geneva Round 3 outcome, and student protest expansion require DAILY monitoring through at least March 6. The system is in maximum-velocity phase. Multiple variables are converging on a ~10-day decision window (Feb 22 to ~March 3). Any individual variable crossing its threshold may cascade the others.",
    "v1.7 NOTE (Session 16): IAEA Board (March 2) creates third independent clock converging with Geneva Round 3 and Trump deadline. This is the tightest multi-clock convergence documented in the project. Student protest expansion (12+ universities) now modeled as independent internal resistance clock (A12.3.6). Caine/Cooper dynamics create new variable in Washington Patience Clock. All three factors require monitoring through at least March 6.",
]

with open(p, "w", encoding="utf-8") as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=200, sort_keys=False)

print(f"Cleaned {len(data['entries'])} entries, {len(data['monitoring_notes'])} monitoring notes")
