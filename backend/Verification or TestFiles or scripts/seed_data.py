"""
Script to seed initial data for testing
Run this to populate the database with sample mood data
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.database import DatabaseService
from services.sentiment_analyzer import SentimentAnalyzer
from models.mood import MoodPoint
from data.cities_200 import CITIES_200
from datetime import datetime
import random

async def seed_data():
    """Seed database with sample mood data"""
    db = DatabaseService()
    analyzer = SentimentAnalyzer()
    
    await db.connect()
    
    # Sample texts with known sentiments
    sample_texts = [
        ("Feeling great about the new project! Excited to see where this goes.", 0.7),
        ("Stressed about the deadline tomorrow. Need to finish everything.", -0.6),
        ("Beautiful weather today. Perfect for a walk in the park.", 0.5),
        ("Anxious about the upcoming exam. Hope I studied enough.", -0.5),
        ("Just got promoted! This is amazing news!", 0.9),
        ("Traffic is terrible today. Going to be late for the meeting.", -0.4),
        ("Love spending time with family. These moments are precious.", 0.8),
        ("Worried about climate change. We need to act now.", -0.3),
        ("Grateful for all the support from friends and colleagues.", 0.6),
        ("Frustrated with the slow internet connection.", -0.5),
    ]
    
    # Use the curated 200 global cities dataset and create one mood point per city
    mood_points = []

    for city in CITIES_200:
        text, _ = random.choice(sample_texts)
        source = random.choice(["reddit", "twitter"])

        # Analyze sentiment for the chosen text
        result = analyzer.analyze(text)

        mood_point = MoodPoint(
            lat=city["lat"],
            lng=city["lng"],
            label=result["label"],
            score=result["score"],
            source=source,
            text=f"{text} — seeded for {city['name']}",
            city_name=city["name"],
            timestamp=datetime.utcnow()
        )

        mood_points.append(mood_point)
    
    # Insert into database (one point per city in CITIES_100)
    await db.insert_moods(mood_points)
    print(f"✅ Seeded {len(mood_points)} mood points (one per curated city)")
    
    # Show statistics
    stats = await db.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"Total points: {stats['total_points']}")
    print(f"By source: {stats['by_source']}")
    print(f"By label: {stats['by_label']}")
    print(f"Average score: {stats['average_score']:.3f}")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_data())

