"""
Test script to verify real data flow (no mock data)
Run this after starting the backend server to test Reddit API → OpenRouter → ElevenLabs
"""

import asyncio
import sys
sys.path.append(".")

from services.social_fetcher import SocialFetcher
from services.sentiment_analyzer import SentimentAnalyzer
from services.summary_generator import summary_generator

async def test_real_data_flow():
    print("=" * 60)
    print("TESTING REAL DATA FLOW - NO MOCK DATA")
    print("=" * 60)
    
    # Test city
    test_city = "Toronto"
    
    print(f"\n1. Testing Reddit API for city: {test_city}")
    print("-" * 60)
    
    social_fetcher = SocialFetcher()
    
    try:
        posts = await social_fetcher.fetch_city_posts(test_city, limit=10)
        print(f"✅ SUCCESS: Fetched {len(posts)} real posts from Reddit")
        print(f"\nSample post:")
        if posts:
            print(f"  Platform: {posts[0].get('platform')}")
            print(f"  Text: {posts[0].get('text')[:100]}...")
            print(f"  Author: {posts[0].get('author')}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("\nMake sure your .env has:")
        print("  REDDIT_CLIENT_ID=...")
        print("  REDDIT_CLIENT_SECRET=...")
        return
    
    print(f"\n2. Testing Sentiment Analysis")
    print("-" * 60)
    
    sentiment_analyzer = SentimentAnalyzer()
    
    if posts:
        result = sentiment_analyzer.analyze(posts[0].get('text', ''))
        print(f"✅ SUCCESS: Analyzed sentiment")
        print(f"  Label: {result['label']}")
        print(f"  Score: {result['score']}")
    
    print(f"\n3. Testing OpenRouter AI Summary Generation")
    print("-" * 60)
    
    # Create mock mood points from posts
    from models.mood import MoodPoint
    from datetime import datetime
    
    mood_points = []
    for post in posts[:5]:  # Use first 5 posts
        text = post.get('text', '')
        sentiment = sentiment_analyzer.analyze(text)
        
        mood_point = MoodPoint(
            lat=0.0,
            lng=0.0,
            label=sentiment['label'],
            score=sentiment['score'],
            source="reddit",
            text=text[:200],
            city_name=test_city,
            timestamp=datetime.utcnow()
        )
        mood_points.append(mood_point)
    
    try:
        summary = await summary_generator.generate_summary(mood_points, city_name=test_city)
        print(f"✅ SUCCESS: Generated AI summary")
        print(f"\nSummary:")
        print(f"  {summary}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("\nMake sure your .env has:")
        print("  OPENROUTER_API_KEY=sk-or-v1-...")
        return
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - REAL DATA FLOW WORKING!")
    print("=" * 60)
    print("\n✅ Reddit API: Working")
    print("✅ Sentiment Analysis: Working")
    print("✅ OpenRouter AI: Working")
    print("\nNote: ElevenLabs audio generation is tested via the API endpoint")
    print("Test it by: curl http://localhost:8000/api/city/summary/audio?city=Toronto")

if __name__ == "__main__":
    asyncio.run(test_real_data_flow())
