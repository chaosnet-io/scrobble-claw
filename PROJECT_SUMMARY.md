# ScrobbleClaw - Build Complete 🐦‍⬛

## What We Built

**ScrobbleClaw** - A minimalist Last.fm musical commentator that:
- Checks your recent tracks every 30 minutes during waking hours (6 AM - midnight)
- Finds hidden patterns across your last 5 songs
- Dives into Wikipedia for producer/director/sample connections  
- Drops one sharp, reference-dense comment when it finds something worth saying
- Persists only the essentials: TSV history + MD insights log

## Architecture Decisions

### Why This Worked (vs. music-intel)
- ✅ **No database** → No schema hell, no ORM overhead
- ✅ **No systemd** → Just cron + script, no process management nightmares
- ✅ **Heartbeat-driven** → Wakes up, works, sleeps (no zombies)
- ✅ **Direct Wikipedia** → Fresh data, no 200MB index files
- ✅ **Pattern-first** → Only speaks when there's an actual connection

### File Structure
```
scrobble-claw/
├── SKILL.md              # Full documentation
├── QUICKSTART.md         # 5-minute setup guide
├── config.json           # Last.fm credentials  
├── config.json.example   # Template
├── data/
│   ├── listening_history.tsv   # Minimal track log
│   ├── insights.md            # Best comments archive
│   └── scrobbleclaw.log       # Debug log
└── scripts/
    ├── scrobbleclaw.py        # Main script (executable)
    ├── run-and-notify.sh      # Wrapper for cron
    └── tests/                 # (ready for future tests)
```

### Cron Configuration
- **Schedule**: Every 30 minutes, 6 AM - 11:59 PM
- **ID**: `scrobbleclaw-wakeup`
- **Action**: `openclaw cron run --jobId 6b234903-5af0-44d0-b219-c51fae72eda6` (manual trigger)

## Technical Details

### Pattern Detection Algorithm
1. Get last 5 scrobbled tracks from Last.fm API
2. For each: search Wikipedia (artist + track)
3. Extract keywords: director, producer, composer, sample, featured, etc.
4. Find keywords appearing in ≥2 tracks
5. Generate comment based on connection type

### Comment Generation Examples
- **Producer match**: "Steve Lillywhite had their hands in all of them..."
- **Director match**: "Stephen R. Johnson directed it... same person behind..."
- **Sample match**: "It's like musical archeology—digging through layers"
- **Fallback**: "[Artist/song] has a rabbit hole worth falling into..."

### Key Features
- User-Agent header for Wikipedia compliance
- Rate limiting (500ms between requests)
- Error handling for API failures
- Deduplication via last check timestamp
- Graceful degradation (silent if no patterns found)

## Setup Remaining

Just two steps to bring it to life:

1. **Add your API key to secrets.env** (Security Best Practice):
   ```bash
   cd /home/nuno/.openclaw
   echo "LASTFM_API_KEY=your_api_key" >> secrets.env
   ```

2. **Add your username to config.json**:
   ```bash
   cd /home/nuno/.openclaw/workspace/skills/scrobble-claw
   edit config.json  # Add username only (API key stays in secrets.env)
   ```

2. **Test it**:
   ```bash
   python3 scripts/scrobbleclaw.py --test-comment
   ```

3. **Wait for the magic** (or manually trigger cron to test)
   ```bash
   openclaw cron run --jobId 6b234903-5af0-44d0-b219-c51fae72eda6
   ```

## Lessons from music-intel's Demise

1. **Complexity kills** → Simple heuristics beat ML when you need reliability
2. **Storage matters** → TSV > SQLite for append-only logs
3. **Wake > Always-on** → Heartbeat pattern prevents zombie hell
4. **Fresh > Cached** → Real-time Wikipedia beats stale index
5. **Speak when you have something to say** → Silence is better than noise

## Future Enhancements (Maybe)

- Genius API for lyrical themes
- MusicBrainz for session musician credits
- Sample detection via WhoSampled
- Mood/era pattern matching
- Voice delivery via TTS (late night "hey, listen to this" moments)

But probably not. The beauty is in the simplicity.

## Stats

- **Lines of code**: ~400
- **Dependencies**: 1 (requests)
- **Database tables**: 0
- **Systemd services**: 0
- **Process zombies**: 0
- **Your Last.fm data points analyzed**: ∞
- **"Holy shit" moments**: TBD

---

**Status**: Ready for Last.fm credentials and battle testing.

**Next action**: Add your creds to config.json and let it rip.
