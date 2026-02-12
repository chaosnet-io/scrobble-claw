#!/usr/bin/env python3
"""
ScrobbleClaw - Your musical commentator familiar

A minimalist Last.fm commenter that finds patterns in your recent listening
and serves up insights that make you *actually listen*.

Usage:
    python3 scrobbleclaw.py --check
    python3 scrobbleclaw.py --test-comment
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests
import re

# --- Configuration ---
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
DATA_DIR = Path(__file__).parent.parent / "data"
HISTORY_PATH = DATA_DIR / "listening_history.tsv"
INSIGHTS_PATH = DATA_DIR / "insights.md"
LOG_PATH = DATA_DIR / "scrobbleclaw.log"

# MusicBrainz configuration
MUSICBRAINZ_BASE = "https://musicbrainz.org/ws/2"
USER_AGENT = "ScrobbleClaw/1.0 (OpenClaw; +https://openclaw.ai)"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# --- Logging ---
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {level}: {message}\n")
    print(f"[{timestamp}] {level}: {message}")

# --- Data Persistence ---
def load_secrets():
    """Load Last.fm API key from .openclaw/secrets.env"""
    secrets_path = Path("/home/nuno/.openclaw/secrets.env")
    try:
        with open(secrets_path) as f:
            for line in f:
                if line.startswith("LASTFM_API_KEY="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        pass
    
    log("LASTFM_API_KEY not found in .openclaw/secrets.env", "ERROR")
    log("Please add: LASTFM_API_KEY=your_api_key", "ERROR")
    sys.exit(1)

def load_config():
    """Load config from config.json"""
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            return {
                'api_key': load_secrets(),
                'username': config.get("lastfm", {}).get("username"),
                'settings': config.get("settings", {})
            }
    except FileNotFoundError:
        log("config.json not found! Please create it with your Last.fm username.", "ERROR")
        sys.exit(1)

def get_last_check_time():
    """Get the last time we checked Last.fm to avoid duplicates"""
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r") as f:
            lines = f.readlines()
            if lines:
                # Skip header, get last entry's timestamp
                for line in reversed(lines[1:]):
                    if line.strip():
                        timestamp = line.split("\t")[0]
                        return datetime.fromisoformat(timestamp)
    return datetime.now() - timedelta(hours=1)

def get_artist_name(track):
    """Safely extract artist name from track data (handles Last.fm API variations)"""
    artist_data = track.get('artist', '')
    if isinstance(artist_data, dict):
        # Try 'name' first (newer API format), then '#text' (older format)
        return artist_data.get('name') or artist_data.get('#text', 'Unknown')
    elif isinstance(artist_data, str):
        return artist_data
    return 'Unknown'

def rotate_history(max_entries=50):
    """Keep only the last N entries in history file"""
    if not HISTORY_PATH.exists():
        return
    
    with open(HISTORY_PATH, "r") as f:
        lines = f.readlines()
    
    if len(lines) <= max_entries + 1:  # +1 for header
        return
    
    # Keep header + last N entries
    header = lines[0]
    recent_entries = lines[-max_entries:]
    
    with open(HISTORY_PATH, "w") as f:
        f.write(header)
        f.writelines(recent_entries)
    
    log(f"Rotated history file: kept last {max_entries} entries")

def save_tracks(tracks):
    """Save tracks to history TSV"""
    write_header = not HISTORY_PATH.exists()
    with open(HISTORY_PATH, "a") as f:
        if write_header:
            f.write("timestamp\tartist\ttrack\tmusic_brainz_id\turl\n")
        for track in tracks:
            timestamp = datetime.fromtimestamp(int(track['date']['uts'])).isoformat()
            artist = get_artist_name(track).replace("\t", " ")
            track_name = track['name'].replace("\t", " ")
            mbid = track.get('mbid', '')
            url = track.get('url', '')
            f.write(f"{timestamp}\t{artist}\t{track_name}\t{mbid}\t{url}\n")
    
    # Rotate to keep file size manageable
    rotate_history(max_entries=50)

def save_insight(insight_text, track_data, source_url):
    """Save a particularly good insight for future reference"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(INSIGHTS_PATH, "a") as f:
        f.write(f"\n## {timestamp}\n\n")
        f.write(f"**Insight**: {insight_text}\n\n")
        f.write(f"**Tracks**: {track_data}\n\n")
        f.write(f"**Source**: {source_url}\n\n")

# --- Last.fm API ---
def get_recent_tracks(api_key, username, limit=10):
    """Fetch recent tracks from Last.fm"""
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getRecentTracks",
        "user": username,
        "api_key": api_key,
        "format": "json",
        "limit": limit,
        "extended": 1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'recenttracks' in data and 'track' in data['recenttracks']:
            tracks = data['recenttracks']['track']
            # Filter out currently playing track (has no 'date')
            return [t for t in tracks if 'date' in t]
        return []
    except Exception as e:
        log(f"Error fetching Last.fm data: {e}", "ERROR")
        return []

# --- Wikipedia/Genius Data Hunting ---
def get_wikipedia_info(query):
    """Search Wikipedia for info about an artist/song/producer"""
    search_url = "https://en.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1
    }
    
    headers = {
        "User-Agent": "ScrobbleClaw/1.0 (OpenClaw; +https://openclaw.ai)"
    }
    
    try:
        search_resp = requests.get(search_url, params=search_params, headers=headers)
        search_resp.raise_for_status()
        search_data = search_resp.json()
        
        if search_data['query']['search']:
            page_title = search_data['query']['search'][0]['title']
            page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
            
            # Get page excerpt
            extract_params = {
                "action": "query",
                "titles": page_title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "format": "json"
            }
            extract_resp = requests.get(search_url, params=extract_params, headers=headers)
            extract_resp.raise_for_status()
            extract_data = extract_resp.json()
            
            pages = extract_data['query']['pages']
            page_id = list(pages.keys())[0]
            if 'extract' in pages[page_id]:
                return {
                    'title': page_title,
                    'url': page_url,
                    'extract': pages[page_id]['extract'][:500]  # First 500 chars
                }
        return None
    except Exception as e:
        log(f"Wikipedia search error for '{query}': {e}", "WARNING")
        return None

def search_for_connection(artist_track_list):
    """Search for an interesting connection across tracks"""
    connections = []
    
    for artist, track in artist_track_list:
        if not artist or artist == 'Unknown':
            log(f"Skipping track with missing artist: {track}", "WARNING")
            continue
            
        # Search for artist info
        artist_info = get_wikipedia_info(f"{artist} (musician)")
        if artist_info:
            connections.append({
                'type': 'artist',
                'query': artist,
                'data': artist_info
            })
        
        # Search for track info
        track_info = get_wikipedia_info(f"{track} {artist} song")
        if track_info:
            connections.append({
                'type': 'track',
                'query': f"{track} by {artist}",
                'data': track_info
            })
            
        time.sleep(0.5)  # Be nice to Wikipedia
    
    return connections

# --- Pattern Finding ---
def find_golden_connection(connections):
    """Find the most interesting pattern across tracks"""
    # Simple heuristic: find shared keywords in extracts
    keywords = ['directed', 'produced', 'composer', 'musician', 'studio', 'album', 
                'sample', 'inspired', 'influenced', 'featured', 'member', 'band']
    
    # Build keyword frequency map
    keyword_hits = {}
    for conn in connections:
        if conn['data']:
            extract = conn['data']['extract'].lower()
            for keyword in keywords:
                if keyword in extract:
                    if keyword not in keyword_hits:
                        keyword_hits[keyword] = []
                    keyword_hits[keyword].append(conn)
    
    # Find keyword that appears in multiple tracks
    for keyword, conns in keyword_hits.items():
        if len(conns) >= 2:
            # We found a connection!
            track_names = [f"{c['query']}" for c in conns[:3]]
            return {
                'keyword': keyword,
                'connections': conns,
                'summary': f"Found shared '{keyword}' across {', '.join(track_names)}"
            }
    
    return None

# --- Comment Generation ---
def extract_name_from_wikipedia_extract(extract):
    """Extract the subject name from a Wikipedia extract (first words before 'is/was')"""
    import re
    # Pattern: "John Smith is an..." or "John Smith (born 1955) is..."
    match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)?)', extract.strip())
    if match:
        return match.group(1)
    return None

def search_musicbrainz_recording(artist, track_name, limit=3):
    """Search MusicBrainz for a recording"""
    query = f'artist:"{artist}" AND recording:"{track_name}"'
    url = f"{MUSICBRAINZ_BASE}/recording"
    params = {
        "query": query,
        "limit": limit,
        "fmt": "json"
    }
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'recordings' in data and data['recordings']:
            return data['recordings'][0]  # Best match
        return None
    except Exception as e:
        log(f"MusicBrainz search error for '{artist} - {track_name}': {e}", "WARNING")
        return None

def get_musicbrainz_performers(recording_id):
    """Get performer relationships for a recording"""
    url = f"{MUSICBRAINZ_BASE}/recording/{recording_id}"
    params = {
        "inc": "artist-rels",
        "fmt": "json"
    }
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        performers = []
        if 'artist-relation-list' in data:
            for rel in data['artist-relation-list']:
                # Look for performer relationships
                rel_type = rel.get('type')
                if rel_type in ['performer', 'instrument', 'vocal']:
                    artist = rel.get('artist', {})
                    attrs = rel.get('attribute-list', [])
                    instrument = attrs[0] if attrs else 'performer'
                    performers.append({
                        'name': artist.get('name'),
                        'id': artist.get('id'),
                        'instrument': instrument,
                        'type': rel_type
                    })
        return performers
    except Exception as e:
        log(f"MusicBrainz performer lookup error: {e}", "WARNING")
        return []

def get_all_performers_for_tracks(tracks):
    """Get all session performers for a list of tracks"""
    all_performers = {}
    
    for track in tracks:
        artist = get_artist_name(track)
        track_name = track.get('name', '')
        
        if not artist or not track_name or artist == 'Unknown':
            continue
            
        key = f"{artist} - {track_name}"
        recording = search_musicbrainz_recording(artist, track_name)
        
        if recording and 'id' in recording:
            performers = get_musicbrainz_performers(recording['id'])
            if performers:
                all_performers[key] = performers
                log(f"Found {len(performers)} performers for {key}")
        
        time.sleep(0.5)  # Rate limit
    
    return all_performers

def find_session_musician_patterns(performer_map):
    """Find session musicians who appear on multiple tracks"""
    musician_counts = {}
    
    # Count occurrences of each performer across tracks
    for track, performers in performer_map.items():
        for p in performers:
            name = p['name']
            if name not in musician_counts:
                musician_counts[name] = {
                    'count': 0,
                    'instrument': p['instrument'],
                    'tracks': []
                }
            musician_counts[name]['count'] += 1
            musician_counts[name]['tracks'].append(track)
    
    # Find musicians who appear on 2+ tracks
    golden_connections = []
    for name, data in musician_counts.items():
        if data['count'] >= 2:
            golden_connections.append({
                'type': 'session_musician',
                'name': name,
                'instrument': data['instrument'],
                'tracks': data['tracks'],
                'count': data['count']
            })
    
    return golden_connections

def extract_context_around_keyword(extract, keyword, window=100):
    """Extract surrounding context when a keyword is found"""
    import re
    pattern = re.compile(r'(.{0,%d})%s(.{0,%d})' % (window, re.escape(keyword), window), re.IGNORECASE)
    match = pattern.search(extract)
    if match:
        before = match.group(1).strip()
        after = match.group(2).strip()
        # Get first sentence after the keyword
        sentence_match = re.search(r'[^.!?]*[.!?]', after)
        if sentence_match:
            return f"{keyword}{sentence_match.group(0)}"
    return keyword

def generate_session_musician_comment(session_connection):
    """Generate comment for MusicBrainz-discovered session musician pattern"""
    name = session_connection['name']
    instrument = session_connection['instrument']
    tracks = session_connection['tracks']
    count = session_connection['count']
    
    track_list = ', '.join(tracks[:3])
    
    # Context based on instrument and count
    if count == 2:
        return f"{track_list}—{name} played {instrument} on both. Same session player, different sessions. Same hands, different studios."
    elif count >= 3:
        return f"{track_list}—{name}'s {instrument} connects all {count} tracks. Session legend with credits spanning decades. The through-line is real."
    else:
        return f"{track_list}—{name} on {instrument}. Professional session player, same hands, different universes."

# Insert this function before generate_comment
# Find the line before 'def generate_comment' and add it there
def generate_comment(golden_connection, recent_tracks):
    """Generate an educational, curiosity-sparking comment with context"""
    if not golden_connection:
        return None
    
    keyword = golden_connection['keyword']
    conn = golden_connection['connections'][0]  # Primary connection
    extract = conn['data']['extract']
    
    if keyword == 'director' or 'directed' in extract.lower():
        # For Wikipedia pages about directors, extract subject name
        director = extract_name_from_wikipedia_extract(extract)
        if director:
            # Find what makes this director interesting
            context = extract_context_around_keyword(extract, director, 150)
            return f"""{conn['query']}—remember that video? {director} directed it. {context[:120]}... Small world when you follow the rabbit hole."""
    
    elif keyword == 'produced' or 'producer' in extract.lower():
        # For Wikipedia pages about producers, extract subject name
        producer = extract_name_from_wikipedia_extract(extract)
        if producer:
            # Extract what they produced and their style
            context = extract_context_around_keyword(extract, producer, 150)
            tracks = [f"{get_artist_name(t)} - {t['name']}" for t in recent_tracks[:3]]
            
            # Add specific context if possible
            if 'brass' in extract.lower() or 'horn' in extract.lower():
                return f"""Funny thing about {', '.join(tracks)}—{producer} shaped both. Neither brass section would be the same without their touch. Check the credits. Same hands, different universes."""
            elif 'drum' in extract.lower() or'rhythm' in extract.lower():
                return f"""Funny thing about {', '.join(tracks)}—{producer} programmed the backbone for both. Those drum patterns didn't happen by accident. Same architect, different buildings."""
            elif 'funk' in extract.lower() or 'soul' in extract.lower():
                return f"""Funny thing about {', '.join(tracks)}—{producer} was in both studios when the magic happened. Same funk sensibility, different decades. The through-line is real."""
            else:
                return f"""Funny thing about {', '.join(tracks)}—{producer} had their hands in all of them. {context[:120]}... Same producer, different universes."""
    
    elif keyword == 'sample':
        # Find what was sampled and from where
        sample_match = re.search(r'sample.*?(["\'])([^"\']+)\1', extract, re.IGNORECASE)
        if sample_match:
            sampled_from = sample_match.group(2)
            return f"""{conn['query']} samples "{sampled_from}"—same source that {golden_connection['connections'][1]['query'] if len(golden_connection['connections']) > 1 else 'another track'} touched. It's like musical archeology, digging through the same layers."""
        else:
            return f"""{conn['query']} samples something that {golden_connection['connections'][1]['query'] if len(golden_connection['connections']) > 1 else 'another track'} also touched. It's like musical archeology—digging through layers."""
    
    elif keyword == 'composer' or 'composed' in extract.lower():
        match = re.search(r'(composer|composed by|composition by).*?([A-Z][a-z]+ [A-Z][a-z]+)', extract, re.IGNORECASE)
        if match:
            composer = match.group(2)
            context = extract_context_around_keyword(extract, composer, 150)
            return f"""{conn['query']}—{composer} wrote that. {context[:120]}... Same composer, different contexts. The melody DNA matches."""
    
    elif 'session musician' in extract.lower() or 'studio musician' in extract.lower():
        match = re.search(r'(session musician|studio musician|musician).*?([A-Z][a-z]+ [A-Z][a-z]+)', extract, re.IGNORECASE)
        if match:
            musician = match.group(2)
            instrument = 'instrument'
            if 'guitar' in extract.lower():
                instrument = 'guitar'
            elif 'bass' in extract.lower():
                instrument = 'bass'
            elif 'drums' in extract.lower():
                instrument = 'drums'
            elif 'piano' in extract.lower() or 'keyboard' in extract.lower():
                instrument = 'keys'
            elif 'horn' in extract.lower() or 'trumpet' in extract.lower():
                instrument ='horn'
            
            tracks = [f"{get_artist_name(t)} - {t['name']}" for t in recent_tracks[:3]]
            return f"""{', '.join(tracks)}—{musician} played {instrument} on both sessions. Same hands, different studios. That's the session musician life."""
    
    else:
        # Generic but intriguing with context
        track = recent_tracks[0]
        # Extract first interesting sentence
        sentences = extract.split('. ')
        interesting_sentence = None
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['known for', 'famous', 'iconic', 'legendary', 'pioneer', 'innovative']):
                interesting_sentence = sentence
                break
        
        if interesting_sentence:
            return f"""Listening to {get_artist_name(track)} - {track['name']}. Here's the rabbit hole: {interesting_sentence[:150]}... One of those musical threads worth pulling."""
        else:
            return f"""Listening to {get_artist_name(track)} - {track['name']}. Here's something to dig into: {extract[:150]}..."""
    
    return None

# --- Main Logic ---
def check_and_comment():
    """Main function: check Last.fm and comment if interesting pattern found"""
    log("Starting ScrobbleClaw check...")
    
    config = load_config()
    api_key = config.get('api_key')
    username = config.get('username')
    
    if not api_key or not username:
        log("Missing Last.fm credentials in config.json", "ERROR")
        return
    
    # Get recent tracks
    last_check = get_last_check_time()
    log(f"Last check: {last_check}")
    
    tracks = get_recent_tracks(api_key, username, limit=10)
    if not tracks:
        log("No tracks found or error occurred")
        return
    
    # Filter to only tracks since last check
    new_tracks = [t for t in tracks if datetime.fromtimestamp(int(t['date']['uts'])) > last_check]
    
    if not new_tracks:
        log("No new tracks since last check")
        return
    
    # Take last 5 unique tracks
    tracks_to_analyze = new_tracks[:5]
    log(f"Analyzing {len(tracks_to_analyze)} tracks: {[t['name'] for t in tracks_to_analyze]}")
    
    # Save to history
    save_tracks(tracks_to_analyze)
    
    # Find connections (Wikipedia-based)
    artist_track_list = [(get_artist_name(t), t['name']) for t in tracks_to_analyze]
    connections = search_for_connection(artist_track_list)
    
    # Also check for session musician patterns (MusicBrainz + correlation)
    session_connections = []
    performer_map = get_all_performers_for_tracks(tracks_to_analyze)
    if performer_map:
        session_patterns = find_session_musician_patterns(performer_map)
        if session_patterns:
            session_connections = session_patterns
            log(f"Found {len(session_patterns)} session musician patterns via MusicBrainz")
    
    # Priority: session musicians are more interesting than generic keywords
    if session_connections:
        # Use the first session connection (most prolific)
        session_conn = session_connections[0]
        comment = generate_session_musician_comment(session_conn)
    else:
        # Fall back to Wikipedia pattern detection
        golden = find_golden_connection(connections)
        if not golden:
            log("No interesting patterns found this time")
            return
        comment = generate_comment(golden, tracks_to_analyze)
    if comment:
        log(f"Generated comment: {comment[:100]}...")
        
        # Save insight
        primary_conn = golden['connections'][0]
        save_insight(comment, ', '.join([f"{get_artist_name(t)} - {t['name']}" for t in tracks_to_analyze[:3]]), primary_conn['data']['url'])
        
        # Send the comment (for manual/cron use)
        print(f"COMMENT_READY: {comment}")
        
        # Return comment for heartbeat handling
        return comment
    else:
        log("Could not generate comment from connection")
    
    return None

def test_comment():
    """Test with sample data"""
    log("=== TEST MODE ===")
    sample_tracks = [
        {'artist': {'#text': 'Peter Gabriel'}, 'name': 'Sledgehammer', 'date': {'uts': str(int(time.time()))}},
        {'artist': {'#text': 'Talking Heads'}, 'name': 'Once in a Lifetime', 'date': {'uts': str(int(time.time() - 300))}},
        {'artist': {'#text': 'David Bowie'}, 'name': 'Modern Love', 'date': {'uts': str(int(time.time() - 600))}},
    ]
    
    artist_track_list = [(t['artist']['#text'], t['name']) for t in sample_tracks]
    connections = search_for_connection(artist_track_list)
    
    if connections:
        golden = find_golden_connection(connections)
        comment = generate_comment(golden, sample_tracks)
        if comment:
            log(f"Test comment: {comment}")
            return comment
    
    return None

# --- CLI ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ScrobbleClaw - Your musical familiar')
    parser.add_argument('--check', action='store_true', help='Check Last.fm and generate comment if patterns found')
    parser.add_argument('--test-comment', action='store_true', help='Test comment generation with sample data')
    
    args = parser.parse_args()
    
    if args.check:
        result = check_and_comment()
        if result:
            print(f"COMMENT_READY: {result}")
    elif args.test_comment:
        test_comment()
    else:
        print("Usage: python3 scrobbleclaw.py --check | --test-comment")
        sys.exit(1)