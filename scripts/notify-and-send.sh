#!/bin/bash
# ScrobbleClaw Notification Wrapper
# Runs the checker and sends message if comment found

# Detect OpenClaw binary path
OPENCLAW_BIN="${OPENCLAW_BIN:-$(which openclaw 2>/dev/null || echo '/home/nuno/.local/bin/openclaw')}"
TELEGRAM_CHAT_ID="${OPENCLAW_CHAT_ID:-8329419968}"

cd /home/nuno/.openclaw/workspace/foundry/scrobble-claw-standalone
OUTPUT=$(python3 scripts/scrobbleclaw.py --check 2>&1)

# Check if a comment was generated
if echo "$OUTPUT" | grep -q "COMMENT_READY:"; then
    COMMENT=$(echo "$OUTPUT" | grep "COMMENT_READY:" | head -1 | sed 's/COMMENT_READY: //')
    
    # Log to file for debugging
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sending comment: $COMMENT" >> data/scrobbleclaw-notifications.log
    
    # Send via Telegram
    "$OPENCLAW_BIN" message send --channel telegram --target "$TELEGRAM_CHAT_ID" --message "$COMMENT"
    
    echo "Sent: $COMMENT"
else
    echo "No comment generated"
fi

# Always log full output for debugging
echo "$OUTPUT" >> data/scrobbleclaw.log
