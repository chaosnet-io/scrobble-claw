#!/usr/bin/env python3
"""Test the new name extraction"""

import sys
sys.path.insert(0, 'scripts')

from scrobbleclaw import get_wikipedia_info, extract_name_from_wikipedia_extract

# Test Steve Lillywhite
producer_info = get_wikipedia_info("Steve Lillywhite (producer)")
if producer_info:
    print("=== Steve Lillywhite Extract ===")
    print(producer_info['extract'][:200])
    print()
    
    name = extract_name_from_wikipedia_extract(producer_info['extract'])
    print(f"Extracted name: {name}")
    
    # Test director
    director_info = get_wikipedia_info("Stephen R. Johnson")
    if director_info:
        print("\n=== Stephen R. Johnson Extract ===")
        print(director_info['extract'][:200])
        print()
        
        name2 = extract_name_from_wikipedia_extract(director_info['extract'])
        print(f"Extracted name: {name2}")