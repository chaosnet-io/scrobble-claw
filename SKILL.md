# ScrobbleClaw

Your personal Last.fm musical commentator that finds the threads connecting your listening and makes you *actually hear* them differently.

## What It Does

Every 30 minutes during waking hours, ScrobbleClaw:
1. Checks your Last.fm recent tracks
2. Analyzes the last 5 songs for hidden connections
3. Dives into Wikipedia/Genius to find producer overlaps, director connections, sample sources
4. Drops one sharp, reference-dense comment
5. Logs the best insights for future reference

**Goal**: Make you pause mid-track and say "wait, what?!"

## Example Comment

> "Sledgehammer—the quintessential Peter Gabriel track. Do you remember the music video with the crazy claymation? Stephen R. Johnson, the director, was also behind the first season of Pee-Wee's Playhouse... who knew?!"

## Installation

1. **Get Last.fm API credentials**:
   - Sign in to Last.fm
   - Go to https://www.last.fm/api/account/create
   - Create an API account to get your API key

2. **Add your API key to secrets.env** (Security Best Practice):
   ```bash
   cd /home/nuno/.openclaw
   echo "LASTFM_API_KEY=your_api_key_here" >> secrets.env
   ```

3. **Configure your Last.fm username**:
   ```bash
   cd /home/nuno/.openclaw/workspace/skills/scrobble-claw
   cp config.json.example config.json
   # Edit config.json with your Last.fm username
   ```

4. **Install dependencies**:
   ```bash
   pip3 install requests
   ```

5. **Enable heartbeat**:
   - Already configured via cron job for every 30 minutes during waking hours

## Configuration

### Secrets (DO NOT commit to git!)
Add to `~/.openclaw/secrets.env`:
```bash
LASTFM_API_KEY=your_api_key_here
```

### Config (Safe to commit)
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

## How It Works

### Data Storage
- **No complex database** - Just simple files:
  - `data/listening_history.tsv` - Track timestamps (auto-rotates to last 50 entries)
  - `data/insights.md` - Best comments archive (grows indefinitely, manual curation)
  - `data/scrobbleclaw.log` - Debug log (manual cleanup)

### Pattern Detection
Looks for connections like:
- Same director/producer across music videos
- Sample sources shared between tracks
- Session musicians appearing across artists
- Unexpected cross-disciplinary work (TV, film, etc.)
- Producer overlaps across different genres

### Comment Style
- Short, punchy, reference-dense
- Makes one specific connection between tracks
- Includes a "go deeper" hook
- Sounds like a music-obsessed friend, not a robot

## Files

```
scrobble-claw/
├── SKILL.md                    # This file
├── QUICKSTART.md               # Quick setup guide
├── PROJECT_SUMMARY.md          # Architecture notes
├── config.json.example         # Credentials template
├── data/
│   ├── listening_history.tsv   # Track history
│   ├── insights.md             # Best comments archive
│   └── scrobbleclaw.log        # Debug log
└── scripts/
    └── scrobbleclaw.py         # Main script
```

## Manual Usage

Test mode (uses sample data):
```bash
cd /home/nuno/.openclaw/workspace/skills/scrobble-claw
python3 scripts/scrobbleclaw.py --test-comment
```

Check Last.fm and generate comment if patterns found:
```bash
python3 scripts/scrobbleclaw.py --check
```

If comment is generated, output will include: `COMMENT_READY: <comment text>`

## Cron Configuration

Heartbeat runs every 30 minutes during waking hours (6:00-23:59):
```cron
*/30 6-23 * * * cd /home/nuno/.openclaw/workspace/skills/scrobble-claw && python3 scripts/scrobbleclaw.py --check
```

## Troubleshooting

**No comments generated**: Not every check finds a pattern. That's normal.

**Wikipedia rate limits**: Script includes delays to be polite. If blocked, wait an hour.

**Last.fm API errors**: Check your API key in secrets.env and username in config.json

**Want more verbose logging**: Check `data/scrobbleclaw.log`

**History file rotation**: TSV auto-rotates to keep last 50 entries. This prevents unbounded growth while keeping recent history for pattern detection.

## Security Notes

⚠️ **IMPORTANT**: Never commit secrets.env or any file containing API keys to git!

- Keep API keys in `~/.openclaw/secrets.env`
- Only username/settings go in `config.json`
- secrets.env is gitignored by default
- config.json is safe to commit

## Philosophy

This is intentionally minimal. We're not building a data warehouse of your listening habits—we're building a delightful familiar that occasionally makes you go "holy shit" mid-song.

Less is more. But when it hits, it hits.
