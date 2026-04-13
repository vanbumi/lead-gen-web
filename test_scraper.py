import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.scraper_cli import scrape_maps_cli
import json

print("=" * 50)
print("TESTING SCRAPER")
print("=" * 50)

# Test dengan berbagai keyword
test_keywords = [
    "cafe",
    "restaurant",
    "hotel in bali",
    "cafe bandung"
]

for keyword in test_keywords:
    print(f"\n🔍 Testing: '{keyword}'")
    print("-" * 30)
    results = scrape_maps_cli(keyword, limit=3)
    print(f"✅ Found: {len(results)} leads")
    if results:
        for i, lead in enumerate(results[:2]):
            print(f"   {i+1}. {lead['Name']}")
            if lead['Address'] != "-":
                print(f"      📍 {lead['Address'][:50]}")
    print()