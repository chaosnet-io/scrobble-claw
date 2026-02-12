#!/usr/bin/env python3
"""Test the new contextual comment generation"""

import sys
sys.path.insert(0, 'scripts')

from scrobbleclaw import generate_comment, get_wikipedia_info

# Test 1: Producer with context
print("=== Test 1: Producer Context ===")
artist_info = get_wikipedia_info("Steve Lillywhite (producer)")
if artist_info:
    golden = {
        'keyword': 'producer',
        'connections': [{
            'type': 'artist',
            'query': 'Peter Gabriel - Sledgehammer',
            'data': artist_info
        }, {
            'type': 'artist', 
            'query': 'Talking Heads - Once in a Lifetime',
            'data': artist_info
        }]
    }
    recent_tracks = [
        {'artist': {'name': 'Peter Gabriel'}, 'name': 'Sledgehammer'},
        {'artist': {'name': 'Talking Heads'}, 'name': 'Once in a Lifetime'},
        {'artist': {'name': 'David Bowie'}, 'name': 'Modern Love'}
    ]
    comment = generate_comment(golden, recent_tracks)
    print(f"Comment: {comment}\n")

# Test 2: Director with context
print("=== Test 2: Director Context ===")
director_info = get_wikipedia_info("Stephen R. Johnson")
if director_info:
    golden = {
        'keyword': 'director',
        'connections': [{
            'type': 'track',
            'query': 'Peter Gabriel - Sledgehammer',
            'data': director_info
        }]
    }
    recent_tracks = [{'artist': {'name': 'Peter Gabriel'}, 'name': 'Sledgehammer'}]
    comment = generate_comment(golden, recent_tracks)
    print(f"Comment: {comment}\n")

print("=== Tests complete ===")