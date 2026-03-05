#!/usr/bin/env bash
# watch_session_log.sh
#
# Watches CLAUDE_SESSION_LOG.md for new Chat Integration Requests and
# invokes Claude Code CLI non-interactively to process them.
#
# Loop prevention: only triggers when the count of "Chat — Integration Request"
# entries increases. Code's own writes (Integration Complete) don't change
# that count, so no feedback loop.
#
# Log rotation: delegates to rotate_session_log.py when file exceeds
# ROTATION_THRESHOLD lines. Rotation commits automatically.
#
# Dependencies: fswatch (brew install fswatch), claude CLI
# State: .claude/watcher_state (last known IR count), .claude/watcher.lock
# Log:   .claude/watcher.log
#
# Run directly for foreground monitoring, or via launchd (install_watcher.sh).

set -euo pipefail

REPO_ROOT="/Volumes/SanDiskSSD/Developer/Repositories/framework"
LOG_FILE="$REPO_ROOT/CLAUDE_SESSION_LOG.md"
STATE_DIR="$REPO_ROOT/.claude"
STATE_FILE="$STATE_DIR/watcher_state"
LOCK_FILE="$STATE_DIR/watcher.lock"
WATCHER_LOG="$STATE_DIR/watcher.log"
ROTATION_THRESHOLD=400  # lines before rotation is triggered

TRIGGER_PATTERN="— Chat — Integration Request"

# Find claude binary — resolve latest installed version dynamically
CLAUDE_BIN=$(ls -1dt "$HOME/Library/Application Support/Claude/claude-code/"*/claude 2>/dev/null | head -1 || true)
if [[ -z "$CLAUDE_BIN" ]]; then
    echo "ERROR: claude CLI not found" >&2
    exit 1
fi

CLAUDE_PROMPT="You are Claude Code for the Iran Transition Project at $REPO_ROOT. \
A new Chat Integration Request has been detected in CLAUDE_SESSION_LOG.md. \
Read the session log, identify any pending requests (Chat Integration Request \
entries not yet followed by a Code Integration Complete), and process them \
per the Staging Directory Protocol in CLAUDE_CODE_INSTRUCTIONS.md. \
Commit all changes atomically and append an Integration Complete entry \
to the session log."

# --- Setup ---
mkdir -p "$STATE_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$WATCHER_LOG"
}

count_requests() {
    grep -c "$TRIGGER_PATTERN" "$LOG_FILE" 2>/dev/null || echo "0"
}

# --- Log rotation ---
rotate_log() {
    local line_count
    line_count=$(wc -l < "$LOG_FILE" | tr -d ' ')
    log "Rotation triggered ($line_count lines > $ROTATION_THRESHOLD threshold)"
    python3 "$REPO_ROOT/scripts/rotate_session_log.py" "$LOG_FILE" \
        && log "Rotation complete" \
        || log "WARNING: rotation failed — skipping (log continues to grow)"
}

# --- Claude invocation ---
process_requests() {
    # Lockfile prevents concurrent runs
    if [[ -f "$LOCK_FILE" ]]; then
        log "Claude already running (lockfile present) — skipping this event"
        return
    fi

    log "Triggering Claude Code (non-interactive)"
    touch "$LOCK_FILE"

    cd "$REPO_ROOT"
    "$CLAUDE_BIN" -p \
        --permission-mode bypassPermissions \
        --model sonnet \
        "$CLAUDE_PROMPT" \
        >> "$WATCHER_LOG" 2>&1 \
        && log "Claude Code run complete" \
        || log "ERROR: Claude Code exited with error (see log above)"

    rm -f "$LOCK_FILE"

    # Update state after run (IR count may have changed if Chat wrote again during run)
    count_requests > "$STATE_FILE"
}

# --- Check file and maybe trigger ---
check_and_trigger() {
    local current_count
    current_count=$(count_requests)
    local last_count=0
    [[ -f "$STATE_FILE" ]] && last_count=$(cat "$STATE_FILE")

    if (( current_count > last_count )); then
        log "Integration Request count: $last_count → $current_count"
        process_requests
    fi

    # Check rotation threshold after processing
    local line_count
    line_count=$(wc -l < "$LOG_FILE" | tr -d ' ')
    if (( line_count > ROTATION_THRESHOLD )); then
        rotate_log
        # Update state after rotation (line numbers shifted)
        count_requests > "$STATE_FILE"
    fi
}

# --- Init ---
if [[ ! -f "$STATE_FILE" ]]; then
    count_requests > "$STATE_FILE"
    log "Initialized: $(cat "$STATE_FILE") existing Integration Request(s)"
fi

log "Watcher started — monitoring $LOG_FILE"
log "Claude binary: $CLAUDE_BIN"

# Check once at startup (in case requests arrived while watcher was down)
check_and_trigger

# Watch for changes — -o aggregates multiple rapid events into one; -l 2 adds
# a 2-second latency to let writes settle before we read the file
fswatch -o -l 2 "$LOG_FILE" | while read -r _; do
    check_and_trigger
done
