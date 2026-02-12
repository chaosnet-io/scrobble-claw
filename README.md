# 🎵 ScrobbleClaw

Your personal Last.fm musical commentator that finds the hidden threads connecting your listening and makes you *actually hear* them differently.

## What It Does

Every 30 minutes during waking hours (configurable), ScrobbleClaw:

1. **Monitors** your Last.fm recent tracks
2. **Analyzes** the last 5-10 songs for hidden connections
3. **Researches** deeper context via Wikipedia and MusicBrainz
4. **Discovers** overlaps: producers, directors, session musicians, sample sources
5. **Comments** with one sharp, reference-dense insight that makes you pause mid-track
6. **Archives** the best insights for future reference

**Goal**: Make you say "wait, what?!" and hear familiar music in a completely new way.

## Example Insight

> "**Sledgehammer**—the quintessential Peter Gabriel track. Do you remember the music video with the crazy claymation? **Stephen R. Johnson**, the director, was also behind the first season of Pee-Wee's Playhouse... who knew?!"

*That connection between an iconic music video and a surreal children's TV show is exactly the kind of thread ScrobbleClaw lives to find.*

## Installation

### Prerequisites

- Python 3.7+
- Last.fm account with API access
- OpenClaw workspace (optional but recommended)

### Quick Setup

```bash
# Clone into your OpenClaw skills directory
cd ~/.openclaw/workspace/skills/
git clone https://github.com/yourusername/scrobble-claw.git scrobble-claw

# Configure your Last.fm credentials
cd scrobble-claw
cp config.json.example config.json
# Edit config.json with your Last.fm username

# Install dependencies
pip install requests

# Add your API key to secrets (outside git!)
echo "LASTFM_API_KEY=your_api_key_here" >> ~/.openclaw/secrets.env
```

### Getting a Last.fm API Key

1. Sign in to Last.fm
2. Create an API account at https://www.last.fm/api/account/create
3. Copy your API key

## Configuration

### `config.json`

```json
{
  "lastfm": {
    "username": "YOUR_LAST_FM_USERNAME"
  },
  "settings": {
    "waking_hours_start": 6,
    "waking_hours_end": 23,
    "check_interval_minutes": 30,
    "tracks_to_analyze": 5
  }
}
```

### `secrets.env` (outside git)

```bash
# ~/.openclaw/secrets.env
LASTFM_API_KEY=your_actual_api_key_here
```

## Manual Usage

Test with sample data (no API calls):

```bash
python3 scripts/scrobbleclaw.py --test-comment
```

Check Last.fm and generate a comment if patterns are found:

```bash
python3 scripts/scrobbleclaw.py --check
```

## How It Works

### Pattern Detection

ScrobbleClaw looks for connections like:

- **Producer overlaps**: Same producer across different artists/genres
- **Session musicians**: Musicians appearing across multiple tracks
- **Director connections**: Music video directors with surprising other works
- **Sample sources**: Tracks sampling the same original recording
- **Studio links**: Same recording studios across different eras
- **Cross-disciplinary work**: Musicians who also worked in TV, film, etc.
- **Genre bridge**: Artists who connect seemingly unrelated genres

### Comment Generation

When a pattern is found:

1. Identifies the shared connection
2. Researches deeper context via MusicBrainz and Wikipedia
3. Crafts a punchy, reference-dense comment
4. Outputs: `COMMENT_READY: <comment text>`
5. Archives best insights to `data/insights.md`

### Data Model

**No complex database** - just simple, auditable files:

- `data/listening_history.tsv` - Track timestamps (auto-rotates to last 50 entries)
- `data/insights.md` - Curated best comments (grows indefinitely)
- `data/scrobbleclaw-notifications.log` - Comment delivery log
- `data/scrobbleclaw.log` - Debug log (not tracked by git)

### Architecture

```
scrobble-claw/
├── README.md                   # This file
├── SKILL.md                     # OpenClaw integration docs
├── QUICKSTART.md                # Quick setup guide
├── PROJECT_SUMMARY.md           # Technical architecture notes
├── config.json.example          # Configuration template
├── .gitignore                   # Excludes logs and cache
├── data/                        # Runtime data (git-tracked except logs)
│   ├── insights.md             # Archive of best comments
│   ├── listening_history.tsv   # Recent track history
│   └── scrobbleclaw-notifications.log
└── scripts/
    ├── scrobbleclaw.py         # Main script
    ├── musicbrainz_utils.py      # MusicBrainz API helpers
    ├── debug_comments.py       # Debug and test utilities
    └── test_*.py               # Various test scripts
```

## Integration with OpenClaw

### Cron/Heartbeat Setup

Add to HEARTBEAT.md:
```
scrobbleclaw-check: Run ScrobbleClaw check for Last.fm patterns and comment if found
```

Or configure a cron job:
```cron
*/30 6-23 * * * cd /path/to/scrobble-claw && python3 scripts/scrobbleclaw.py --check
```

### Manual Trigger

From OpenClaw CLI:
```bash
openclaw gateway wake "scrobbleclaw-check"
```

## Philosophy

ScrobbleClaw is intentionally minimal. We're not building a data warehouse of your listening habits—we're building a delightful familiar that occasionally makes you go "holy shit" mid-song.

Less is more. But when it hits, it hits.

## Troubleshooting

**No comments generated**: Not every check finds a pattern. That's normal and intentional.

**API rate limits**: ScrobbleClaw includes delays to be polite. If you hit limits, wait an hour or adjust check frequency.

**Want more verbose logging**: Check `data/scrobbleclaw.log` (created at runtime)

**Need to reset history**: Delete or archive `data/listening_history.tsv` to start fresh

## Security Notes

- **Never commit secrets.env or keys**
- All API keys belong in `~/.openclaw/secrets.env` (outside workspace)
- Log files are intentionally not tracked by git
- Review `.gitignore` before adding sensitive data

## Contributing

This is a personal familiar tool, but contributions welcome:

1. Fork and create a feature branch
2. Add tests for new pattern detection logic
3. Update documentation
4. Submit pull request

## License

MIT License - feel free to adapt for your own familiar

## Future Ideas

- [ ] Discord/Slack channel integration options
- [ ] More sophisticated pattern detection algorithms
- [ ] Configurable comment persona (music critic, music nerd, etc.)
- [ ] Async processing for faster response
- [ ] Historical analysis mode (not just recent tracks)
- [ ] Multi-user support

---

*Built with Python, curiosity, and the joy of discovering that the bassist from your favorite 90s alt-rock band also played on a Motown track you've heard 1000 times.*