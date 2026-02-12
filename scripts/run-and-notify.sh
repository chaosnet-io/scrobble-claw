#!/bin/bash
# ScrobbleClaw Runner - Runs the check and sends notification if comment generated

cd /home/nuno/.openclaw/workspace/skills/scrobble-claw
OUTPUT=$(python3 scripts/scrobbleclaw.py --check 2>&1)

# Check if a comment was generated
if echo "$OUTPUT" | grep -q "COMMENT_READY:"; then
    COMMENT=$(echo "$OUTPUT" | grep "COMMENT_READY:" | sed 's/COMMENT_READY: //')
    
    # Send via Telegram (adjust channel as needed)
    /usr/local/bin/openclaw message send --channel telegram --target NunoPovoa --message "$COMMENT"
fi

# Log output
echo "$OUTPUT" >> data/scrobbleclaw.log