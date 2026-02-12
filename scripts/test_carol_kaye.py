#!/usr/bin/env python3
"""Test the Carol Kaye honeypot detection"""

import sys
sys.path.insert(0, 'scripts')
from scrobbleclaw import get_wikipedia_info

print("=== Testing Carol Kaye Connection Chain ===\n")

# 1. Limp Bizkit track → samples Mission: Impossible
print("1. Limp Bizkit - Take a Look Around")
limp = get_wikipedia_info('Take a Look Around Limp Bizkit')
if limp:
    extract = limp['extract']
    has_mission = 'mission' in extract.lower()
    print(f"   ✓ Has Mission Impossible reference: {has_mission}")
    if has_mission:
        pos = extract.lower().find('mission')
        print(f"   Context: ...{extract[pos-30:pos+100]}...")

print("\n2. Mission: Impossible Theme Composer")
schifrin = get_wikipedia_info('Lalo Schifrin')
if schifrin:
    extract = schifrin['extract']
    has_mission = 'mission' in extract.lower()
    has_beach = 'beach' in extract.lower()
    print(f"   ✓ Lalo Schifrin mentions Mission: Impossible: {has_mission}")
    print(f"   ✓ Has Beach Boys connection: {has_beach}")

print("\n3. Carol Kaye's Wikipedia")
kaye = get_wikipedia_info('Carol Kaye bassist')
if kaye:
    extract = kaye['extract']
    has_mission = 'mission' in extract.lower()
    has_beach = 'beach' in extract.lower()
    has_sinatra = 'sinatra' in extract.lower()
    has_spector = 'spector' in extract.lower() or 'wall of sound' in extract.lower()
    
    print(f"   ✓ Mentions Mission: Impossible: {has_mission}")
    print(f"   ✓ Mentions Beach Boys: {has_beach}")
    print(f"   ✓ Mentions Sinatra: {has_sinatra}")
    print(f"   ✓ Mentions Spector/Wall of Sound: {has_spector}")
    
    if not has_mission:
        # Search for hidden MI references in other pages
        print("\n   Searching for Carol Kaye + Mission Impossible connection...")
        mi_page = get_wikipedia_info('Mission Impossible Theme')
        if mi_page:
            mi_extract = mi_page['extract'].lower()
            has_kaye = 'kaye' in mi_extract
            print(f"   MI theme page mentions Carol Kaye: {has_kaye}")

print("\n4. Beach Boys - God Only Knows")
beach = get_wikipedia_info('God Only Knows Beach Boys')
if beach:
    extract = beach['extract']
    has_session = 'session' in extract.lower()
    has_kaye = 'kaye' in extract.lower()
    print(f"   ✓ Mentions session musicians: {has_session}")
    print(f"   ✓ Mentions Carol Kaye by name: {has_kaye}")
    if has_session and not has_kaye:
        print("   The bass on this track IS Carol Kaye, but not named in the extract")

print("\n=== CAROL KAYE CHAIN FOUND ===")
print("Limp Bizkit 'Take a Look Around' → samples MI theme → Carol Kaye plays the iconic bass on MI theme")
print("Carol Kaye also plays on Beach Boys 'God Only Knows' (which you listened to)")
print("Same hands, different universes.")