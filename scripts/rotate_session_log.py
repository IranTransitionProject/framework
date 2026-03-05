#!/usr/bin/env python3
"""rotate_session_log.py

Prunes resolved entry pairs from CLAUDE_SESSION_LOG.md.

A "resolved pair" is a Chat Integration Request immediately followed
(as the next entry) by a Code Integration Complete. Resolved pairs are
removed from the live log; git history preserves the full record.

A rotation cleanup entry is appended before committing so both sides
know what was pruned.

Usage:
    python3 scripts/rotate_session_log.py CLAUDE_SESSION_LOG.md

Exit codes:
    0 — rotation performed and committed
    1 — no resolved pairs found (nothing to do, not an error)
    2 — error
"""

import re
import sys
import subprocess
from datetime import date
from pathlib import Path

LOG_SECTION_HEADER = "## Log"
END_MARKER = "<!-- END LOG -->"
ENTRY_RE = re.compile(
    r"^(### \d{4}-\d{2}-\d{2} — (?:Chat|Code) — .+)$",
    re.MULTILINE,
)


def split_log(content: str) -> tuple[str, str]:
    """Split file into protocol header and log body."""
    idx = content.find(LOG_SECTION_HEADER)
    if idx == -1:
        raise ValueError(f'"{LOG_SECTION_HEADER}" marker not found in log file')
    return content[: idx + len(LOG_SECTION_HEADER)], content[idx + len(LOG_SECTION_HEADER) :]


def parse_entries(body: str) -> list[dict]:
    """Parse log body into a list of entry dicts with keys: header, text, is_chat_ir, is_code_ic."""
    matches = list(ENTRY_RE.finditer(body))
    entries = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        text = body[start:end].rstrip("\n")
        header = m.group(1)
        entries.append(
            {
                "header": header,
                "text": text,
                "is_chat_ir": "— Chat —" in header and "Integration Request" in header,
                "is_code_ic": "— Code —" in header and "Integration Complete" in header,
            }
        )
    return entries


def find_resolved_indices(entries: list[dict]) -> set[int]:
    """Return indices of matched Chat IR + Code IC pairs."""
    resolved = set()
    for i, entry in enumerate(entries):
        if entry["is_chat_ir"] and i + 1 < len(entries):
            if entries[i + 1]["is_code_ic"]:
                resolved.add(i)
                resolved.add(i + 1)
    return resolved


def build_cleanup_entry(pruned_count: int) -> str:
    today = date.today().strftime("%Y-%m-%d")
    return (
        f"### {today} — Code — Cleanup\n\n"
        f"**Log rotation.** Pruned {pruned_count} resolved pair(s) "
        f"(Chat Integration Request + Code Integration Complete). "
        f"Git history preserves full record.\n"
    )


def rotate(log_path: Path) -> bool:
    """Rotate the log. Returns True if rotation was performed."""
    content = log_path.read_text(encoding="utf-8")
    header, body = split_log(content)

    entries = parse_entries(body)
    if not entries:
        print("No entries found — nothing to rotate")
        return False

    resolved = find_resolved_indices(entries)
    if not resolved:
        print("No resolved pairs found — nothing to prune")
        return False

    kept = [e for i, e in enumerate(entries) if i not in resolved]
    pruned_pairs = len(resolved) // 2

    # Reconstruct: header + blank line + kept entries + cleanup entry + END marker
    kept_text = "\n\n".join(e["text"] for e in kept)
    cleanup = build_cleanup_entry(pruned_pairs)

    new_content = (
        header
        + ("\n\n" if kept_text else "\n\n")
        + (kept_text + "\n\n" if kept_text else "")
        + cleanup
        + "\n"
        + END_MARKER
        + "\n"
    )

    log_path.write_text(new_content, encoding="utf-8")
    print(f"Pruned {pruned_pairs} resolved pair(s) — {len(kept)} entries remain")

    # Commit
    repo_root = log_path.parent
    subprocess.run(["git", "add", str(log_path)], cwd=repo_root, check=True)
    subprocess.run(
        [
            "git", "commit", "-m",
            (
                f"Session log rotation: pruned {pruned_pairs} resolved pair(s)\n\n"
                f"Git history preserves full record.\n\n"
                f"Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
            ),
        ],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(["git", "push"], cwd=repo_root, check=True)
    print("Committed and pushed rotation")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} CLAUDE_SESSION_LOG.md", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    try:
        performed = rotate(path)
        sys.exit(0 if performed else 1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
