#!/usr/bin/env python3
"""Debug the keyword detection"""

import sys
sys.path.insert(0, 'scripts')

from scrobbleclaw import get_wikipedia_info, find_golden_connection

# Get Wikipedia data
producer_info = get_wikipedia_info("Steve Lillywhite (producer)")
if producer_info:
    print("=== Steve Lillywhite Extract (first 300 chars) ===")
    print(producer_info['extract'][:300])
    print()
    
    # Build connections like the real code does
    connections = []
    extract_lower = producer_info['extract'].lower()
    
    print("=== Keyword matches in extract ===")
    keywords = ['directed', 'produced', 'composer', 'musician', 'studio', 'album', 
                'sample', 'inspired', 'influenced', 'featured', 'member', 'band']
    
    for kw in keywords:
        if kw in extract_lower:
            print(f"✓ Found: '{kw}'")
            
    print()
    print("=== Testing name extraction ===")
    from scrobbleclaw import extract_name_near_keyword
    
    name = extract_name_near_keyword(producer_info['extract'], 'produced by')
    print(f"Name near 'produced by': {name}")
    
    name2 = extract_name_near_keyword(producer_info['extract'], 'producer')
    print(f"Name near 'producer': {name2}")