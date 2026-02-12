#!/usr/bin/env python3
"""Improved MusicBrainz search for session musicians"""

import sys
sys.path.insert(0, 'scripts')
from musicbrainz_utils import search_recording, get_recording_performers
from scrobbleclaw import get_wikipedia_info

print("=== MusicBrainz Session Musician Hunt ===\n")

tracks_to_check = [
    ("Limp Bizkit", "Take a Look Around"),
    ("The Beach Boys", "God Only Knows"), 
    ("Mission: Impossible", "Theme"),
    ("Lalo Schifrin", "Mission: Impossible Theme"),
]

# Note: MusicBrainz performer data is user-contributed and incomplete
# especially for 1960s session work, which is why Wikipedia + research is needed

for artist, track in tracks_to_check:
    print(f"Testing: {artist} - {track}")
    recording = search_recording(artist, track, limit=5)
    if recording:
        print(f"  Recording ID: {recording.get('id')}")
        print(f"  Title: {recording.get('title')}")
        print(f"  Artist: {recording.get('artist', {}).get('name', 'Unknown')}")
        
        performers = get_recording_performers(recording['id'])
        if performers:
            print(f"  Performers found: {len(performers)}")
            for p in performers:
                print(f"    - {p['name']} ({p['instrument']})")
        else:
            print("  No performer data in MusicBrainz")
    else:
        print("  No recording found in MusicBrainz")
    print()

# Alternative approach - manual knowledge base
print("=== Manual Wrecking Crew Knowledge ===")
print("Based on music history research (not just Wikipedia):")
print()
print("Carol Kaye played on:")
print("✓ Mission: Impossible theme (bass)")  
print("✓ Beach Boys - Pet Sounds/God Only Knows (bass)")
print("✓ Sonny & Cher 'The Beat Goes On' (guitar/bass)")
print("✓ Sinatra 'These Boots Are Made for Walking' (bass)")
print("✓ 10,000+ other tracks")
print()
print("Hal Blaine played drums on:")
print("✓ 40 #1 hits (The Beach Boys, Sinatra, etc.)")
print("✓ Countless 60s classics")
print()
print("The Wrecking Crew underpin most 1960s hits")

# Conclusion
print("\n=== TAKEAWAY ===")
print("MusicBrainz performer data is INCOMPLETE for pre-1970s session work.")
print("To catch Carol Kaye/The Wrecking Crew, we need:")
print("1. Manual knowledge base of legendary session players")
print("2. Pattern matching tracks to known session credits")
print("3. Wikipedia deeper links (sampling discoveries + session lore)")
print("4. Hybrid approach: MusicBrainz for modern + knowledge base for classics")