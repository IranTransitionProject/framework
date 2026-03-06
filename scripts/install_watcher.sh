#!/usr/bin/env bash
# install_watcher.sh
#
# Installs the session log watcher as a macOS launchd agent.
# Idempotent — safe to re-run after updates to watch_session_log.sh.
#
# Usage: bash scripts/install_watcher.sh
#
# To uninstall:
#   launchctl unload ~/Library/LaunchAgents/org.irantransitionproject.session-watcher.plist
#   rm ~/Library/LaunchAgents/org.irantransitionproject.session-watcher.plist

set -euo pipefail

REPO_ROOT="/Volumes/SanDiskSSD/Developer/Repositories/framework"
PLIST_LABEL="org.irantransitionproject.session-watcher"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"
WATCH_SCRIPT="$REPO_ROOT/scripts/watch_session_log.sh"

# --- Dependency checks ---
if ! command -v fswatch &>/dev/null; then
    echo "ERROR: fswatch not found. Install with: brew install fswatch"
    exit 1
fi

CLAUDE_BIN=$(ls -1dt "$HOME/Library/Application Support/Claude/claude-code/"*/claude 2>/dev/null | head -1 || true)
if [[ -z "$CLAUDE_BIN" ]]; then
    echo "ERROR: claude CLI not found under ~/Library/Application Support/Claude/claude-code/"
    exit 1
fi

chmod +x "$WATCH_SCRIPT"

# Build PATH for launchd (it doesn't inherit the user's shell PATH)
LAUNCHD_PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# --- Write plist ---
# Uses WatchPaths so launchd triggers the script on each file change
# (native kqueue — no fswatch needed). The script runs once, processes
# any new Integration Requests, then exits. launchd restarts it on the
# next file change. No RunAtLoad, no KeepAlive, no WorkingDirectory.
cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$WATCH_SCRIPT</string>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$LAUNCHD_PATH</string>
        <key>HOME</key>
        <string>$HOME</string>
    </dict>

    <!-- Trigger on session log file changes (native kqueue, no fswatch needed) -->
    <key>WatchPaths</key>
    <array>
        <string>$REPO_ROOT/CLAUDE_SESSION_LOG.md</string>
    </array>

    <!-- Prevent hammering if something loops: min 5s between runs -->
    <key>ThrottleInterval</key>
    <integer>5</integer>

    <!-- Capture output before script's own exec redirect takes over -->
    <key>StandardOutPath</key>
    <string>$REPO_ROOT/.claude/watcher.log</string>
    <key>StandardErrorPath</key>
    <string>$REPO_ROOT/.claude/watcher.log</string>
</dict>
</plist>
EOF

echo "Plist written: $PLIST_PATH"

# --- Load / reload agent ---
# Unload first if already running (idempotent)
launchctl unload "$PLIST_PATH" 2>/dev/null && echo "Stopped existing agent" || true
launchctl load "$PLIST_PATH"

echo ""
echo "Watcher agent installed and running."
echo "  PList:  $PLIST_PATH"
echo "  Log:    $REPO_ROOT/.claude/watcher.log"
echo ""
echo "To check status:  launchctl list | grep irantransitionproject"
echo "To tail log:      tail -f $REPO_ROOT/.claude/watcher.log"
echo "To uninstall:     launchctl unload $PLIST_PATH && rm $PLIST_PATH"
