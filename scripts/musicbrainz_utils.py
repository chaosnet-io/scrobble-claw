#!/usr/bin/env python3
"""
MusicBrainz utilities for ScrobbleClaw

Looks up performer relationships to catch session musicians like Carol Kaye
"""

import requests
import time
from urllib.parse import quote

MUSICBRAINZ_BASE = "https://musicbrainz.org/ws/2"
USER_AGENT = "ScrobbleClaw/1.0 (OpenClaw; +https://openclaw.ai)"

def search_recording(artist, track_name, limit=3):
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
        print(f"MusicBrainz search error: {e}")
        return None

def get_recording_performers(recording_id):
    """Get performer relationships for a recording"""
    url = f"{MUSICBRAINZ_BASE}/recording/{quote(recording_id)}"
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
                if rel.get('type') in ['performer', 'instrument', 'vocal']:
                    artist = rel.get('artist', {})
                    instrument = rel.get('attribute-list', ['performer'])[0]
                    performers.append({
                        'name': artist.get('name'),
                        'id': artist.get('id'),
                        'instrument': instrument
                    })
        return performers
    except Exception as e:
        print(f"MusicBrainz performer lookup error: {e}")
        return []

def find_carol_kaye_connections(tracks):
    """Check if Carol Kaye appears in any of these tracks"""
    connections = []
    
    for track in tracks:
        artist = track.get('artist', {})
        if isinstance(artist, dict):
            artist_name = artist.get('name')
        else:
            artist_name = str(artist)
            
        track_name = track.get('name')
        
        if not artist_name or not track_name:
            continue
            
        print(f"Searching MusicBrainz: {artist_name} - {track_name}")
        recording = search_recording(artist_name, track_name)
        
        if recording and 'id' in recording:
            performers = get_recording_performers(recording['id'])
            print(f"  Found performers: {[p['name'] for p in performers]}")
            
            # Check for Carol Kaye specifically
            for performer in performers:
                if 'Kaye' in performer['name'] or 'Carol' in performer['name']:
                    connections.append({
                        'track': f"{artist_name} - {track_name}",
                        'performer': performer['name'],
                        'instrument': performer['instrument'],
                        'type': 'session_musician'
                    })
        
        time.sleep(1)  # Be nice to MusicBrainz
    
    return connections

# Test the honeypot
if __name__ == "__main__":
    print("=== Testing Carol Kaye Detection ===\n")
    
    test_tracks = [
        {'artist': {'name': 'Limp Bizkit'}, 'name': 'Take a Look Around'},
        {'artist': {'name': 'The Beach Boys'}, 'name': 'God Only Knows'},
        {'artist': {'name': 'James Brown'}, 'name': "Papa's Got A Brand New Bag"},
    ]
    
    connections = find_carol_kaye_connections(test_tracks)
    
    if connections:
        print(f"\n🎉 FOUND {len(connections)} Carol Kaye connections!")
        for conn in connections:
            print(f"   {conn['track']} → {conn['performer']} on {conn['instrument']}")
    else:
        print("\nNo Carol Kaye connections found in test tracks")
        print("This suggests the data might not be complete in MusicBrainz")