import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from data.cities_200 import CITIES_200

print(f"Total cities in dataset: {len(CITIES_200)}")

# Check for duplicates
seen = set()
duplicates = []
for city in CITIES_200:
    if city['name'] in seen:
        duplicates.append(city['name'])
    seen.add(city['name'])

if duplicates:
    print(f"Found {len(duplicates)} duplicate(s): {duplicates}")
else:
    print("No duplicates found!")
