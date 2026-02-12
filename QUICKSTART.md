# ScrobbleClaw Quick Start

## Setup (5 Minutes)

### 1. Get Your Last.fm API Key
- Go to https://www.last.fm/api/account/create
- Fill out the form:
  - API Name: `ScrobbleClaw`
  - API Description: `Personal musical commentary tool`
  - Callback URL: leave blank
- Click submit
- Copy your **API Key** (32 characters)

### 2. Store Your API Key Securely

⚠️ **Security Best Practice**: Never store API keys in config files!

```bash
cd /home/nuno/.openclaw
echo "LASTFM_API_KEY=your_api_key_here" >> secrets.env
```

### 3. Configure Your Username

```bash
cd /home/nuno/.openclaw/workspace/skills/scrobble-claw
```

Edit `config.json`:
```json
{
  "lastfm": {
    "username": "YOUR_LAST_FM_USERNAME"
  },
  "settings": {
    "waking_hours_start": 6,
    "waking_hours_end": 23,
    "check_interval_minutes": 30
  }
}
```

### 4. Install Dependencies
```bash
pip3 install requests
```

### 5. Test It
```bash
cd /home/nuno/.openclaw/workspace/skills/scrobble-claw
python3 scripts/scrobbleclaw.py --test-comment
```

You should see a test comment about Steve Lillywhite producing Peter Gabriel, Talking Heads, etc.

### 6. Manual Check (After You've Scrobbled Some Music)
```bash
python3 scripts/scrobbleclaw.py --check
```

If it finds a pattern, you'll see:
```
COMMENT_READY: <your insightful comment here>
```

### 7. That's It!

The cron job is already configured to run every 30 minutes between 6 AM and 11:59 PM. When it finds something interesting, you'll get a message.

## Configuration Files

### Where Things Live

**Secret (never commit):**
- Location: `~/.openclaw/secrets.env`
- Contains: `LASTFM_API_KEY=your_key_here`
- Gitignored: ✅ Yes

**Config (safe to commit):**
- Location: `skills/scrobble-claw/config.json`
- Contains: Username, settings only
- Gitignored: ❌ No (safe to version control)

### Why This Matters

- **Security**: API keys in secrets.env won't be exposed if you share your config
- **Portability**: You can share config.json templates without exposing keys
- **Best Practices**: Separates secrets from configuration

## How to Know It's Working

- Check the log: `tail -f data/scrobbleclaw.log`
- Check history: `cat data/listening_history.tsv`
- Check insights: `cat data/insights.md` (only the best comments)

## Troubleshooting

**"No tracks found"**
- Make sure you're scrobbling to Last.fm!
- Check your username in config.json

**Wikipedia errors**
- Normal if rate limited, will retry next check
- Script is polite with delays built in

**No comments for days**
- Not every listening session has a "holy shit" connection
- That's by design—quality over quantity
- Check insights.md to see past gems

## Security Checklist

- [ ] API key added to `~/.openclaw/secrets.env`
- [ ] Username configured in `config.json`
- [ ] secrets.env is in .gitignore (should be by default)
- [ ] config.json does NOT contain API key
- [ ] No credentials committed to git

## Uninstall

Just delete the directory:
```bash
rm -rf /home/nuno/.openclaw/workspace/skills/scrobble-claw
```

And remove the cron job:
```bash
# List cron jobs
openclaw cron list

# Remove scrobbleclaw-wakeup (use the ID)
openclaw cron remove --jobId <id>
```
