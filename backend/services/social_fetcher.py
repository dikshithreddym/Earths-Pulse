"""
Social Media Data Fetcher
Fetches posts from Reddit and Twitter with location data
"""

import os
import praw
import tweepy
from typing import List, Dict
from dotenv import load_dotenv
import random
import asyncio
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

class SocialMediaFetcher:
    """Fetches posts from social media platforms"""
    
    def __init__(self):
        self.reddit_client = None
        self.twitter_client = None
        self.executor = ThreadPoolExecutor(max_workers=5)  # Add executor
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Reddit and Twitter API clients"""
        # Reddit (PRAW)
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        reddit_secret = os.getenv("REDDIT_CLIENT_SECRET")
        reddit_user_agent = os.getenv("REDDIT_USER_AGENT", "EarthPulse/1.0")
        
        if reddit_client_id and reddit_secret:
            try:
                self.reddit_client = praw.Reddit(
                    client_id=reddit_client_id,
                    client_secret=reddit_secret,
                    user_agent=reddit_user_agent
                )
                print("✅ Reddit client initialized")
            except Exception as e:
                print(f"⚠️ Error initializing Reddit: {e}")
        
        # Twitter (Tweepy)
        twitter_bearer = os.getenv("TWITTER_BEARER_TOKEN")
        if twitter_bearer:
            try:
                self.twitter_client = tweepy.Client(bearer_token=twitter_bearer)
                print("✅ Twitter client initialized")
            except Exception as e:
                print(f"⚠️ Error initializing Twitter: {e}")
    
    def is_ready(self) -> bool:
        """Check if at least one social media client is ready"""
        return self.reddit_client is not None or self.twitter_client is not None
    
    async def fetch_recent_posts(self, limit: int = 50, reddit_only: bool = False) -> List[Dict]:
        """
        Fetch recent posts from all available social media platforms
        
        Args:
            limit: Maximum number of posts to fetch
            reddit_only: If True, only use Reddit (ignore Twitter)
            
        Returns:
            List of post dictionaries with text, location, and source
        """
        posts = []
        
        # Fetch from Reddit
        if self.reddit_client:
            try:
                reddit_posts = await self._fetch_reddit_posts(limit // 2)
                posts.extend(reddit_posts)
            except Exception as e:
                print(f"Error fetching Reddit posts: {e}")
        
        # Fetch from Twitter
        if (not reddit_only) and self.twitter_client:
            try:
                twitter_posts = await self._fetch_twitter_posts(limit // 2)
                posts.extend(twitter_posts)
            except Exception as e:
                print(f"Error fetching Twitter posts: {e}")
        
        # If no API clients available, use mock data
        if not posts:
            posts = self._generate_mock_posts(limit)
        
        return posts[:limit]

    async def fetch_reddit_city_posts(self, cities: List[Dict], per_city: int = 1) -> List[Dict]:
        """Fetch recent Reddit posts and map them to specific cities.

        For each city in the provided list, attempts to find up to `per_city` Reddit posts
        that mention the city name. Returns ONLY real Reddit data, no fallbacks.

        Each returned dict contains: text, lat, lng, source, timestamp, city_name
        """
        results: List[Dict] = []

        if not self.reddit_client:
            raise Exception("Reddit API not configured. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")

        try:
            for city in cities:
                city_name = city["name"]
                query = f'"{city_name}" (feeling OR mood OR today OR weather OR traffic OR happy OR sad OR stressed OR life)'
                found_count = 0

                try:
                    # Run PRAW call in thread pool to avoid warnings
                    loop = asyncio.get_event_loop()
                    submissions = await loop.run_in_executor(
                        self.executor,
                        lambda: list(self.reddit_client.subreddit("all").search(
                            query=query,
                            limit=max(5, per_city * 2),
                            sort="new",
                            time_filter="day",
                        ))
                    )
                    
                    for submission in submissions:
                        text = submission.title
                        if hasattr(submission, 'selftext') and submission.selftext:
                            text += " " + (submission.selftext or "")
                        text = (text or "").strip()
                        
                        # Skip short or empty posts
                        if not text or len(text) < 20:
                            continue

                        results.append({
                            "text": text[:500],
                            "lat": city["lat"],
                            "lng": city["lng"],
                            "source": "reddit",
                            "timestamp": datetime.utcnow(),
                            "city_name": city_name,
                        })
                        found_count += 1
                        if found_count >= per_city:
                            break
                except Exception as e:
                    print(f"Reddit search error for {city_name}: {e}")

        except Exception as e:
            print(f"Error in fetch_reddit_city_posts: {e}")
            raise

        if not results:
            raise Exception("No Reddit posts found for any cities. Check Reddit API credentials or try different cities.")

        return results
    
    async def _fetch_reddit_posts(self, limit: int) -> List[Dict]:
        """Fetch posts from Reddit"""
        posts = []
        
        try:
            # Fetch from popular subreddits
            subreddits = ["worldnews", "news", "todayilearned", "mildlyinteresting", "Showerthoughts"]
            
            for subreddit_name in subreddits[:2]:  # Limit to avoid rate limits
                subreddit = self.reddit_client.subreddit(subreddit_name)
                
                for submission in subreddit.hot(limit=limit // len(subreddits[:2])):
                    # Extract text (title + selftext)
                    text = submission.title
                    if hasattr(submission, 'selftext') and submission.selftext:
                        text += " " + submission.selftext
                    
                    # Get location (mock for now - Reddit doesn't provide location)
                    # In production, you'd use geocoding or user profile data
                    lat, lng = self._get_random_location()
                    
                    posts.append({
                        "text": text[:500],  # Limit text length
                        "lat": lat,
                        "lng": lng,
                        "source": "reddit",
                        "timestamp": datetime.utcnow()
                    })
                    
                    if len(posts) >= limit:
                        break
                
                if len(posts) >= limit:
                    break
        except Exception as e:
            print(f"Error in Reddit fetch: {e}")
        
        return posts
    
    async def _fetch_twitter_posts(self, limit: int) -> List[Dict]:
        """Fetch posts from Twitter/X"""
        posts = []
        
        try:
            # Search for recent tweets (example query)
            query = "lang:en -is:retweet"  # English, not retweets
            
            tweets = self.twitter_client.search_recent_tweets(
                query=query,
                max_results=min(limit, 100),  # Twitter API limit
                tweet_fields=["created_at", "text", "geo"]
            )
            
            if tweets.data:
                for tweet in tweets.data:
                    text = tweet.text
                    
                    # Try to get location from tweet geo or use random
                    if tweet.geo:
                        # Extract from geo if available
                        lat, lng = self._get_random_location()  # Placeholder
                    else:
                        lat, lng = self._get_random_location()
                    
                    posts.append({
                        "text": text[:500],
                        "lat": lat,
                        "lng": lng,
                        "source": "twitter",
                        "timestamp": datetime.utcnow()
                    })
        except Exception as e:
            print(f"Error in Twitter fetch: {e}")
        
        return posts
    
    def _get_random_location(self) -> tuple:
        """
        Generate a random location (lat, lng)
        In production, use geocoding services or user location data
        """
        # Random locations weighted towards populated areas
        major_cities = [
            (40.7128, -74.0060),   # New York
            (34.0522, -118.2437),  # Los Angeles
            (51.5074, -0.1278),    # London
            (35.6762, 139.6503),   # Tokyo
            (-33.8688, 151.2093),  # Sydney
            (28.6139, 77.2090),    # Delhi
            (-23.5505, -46.6333),  # São Paulo
            (55.7558, 37.6173),    # Moscow
            (48.8566, 2.3522),     # Paris
            (39.9042, 116.4074),   # Beijing
        ]
        
        # 70% chance of major city, 30% random
        if random.random() < 0.7:
            return random.choice(major_cities)
        else:
            return (
                random.uniform(-90, 90),
                random.uniform(-180, 180)
            )
    
    def _generate_mock_posts(self, limit: int) -> List[Dict]:
        """Generate mock posts - REMOVED, we only use real data now"""
        raise Exception("Mock data generation is disabled. Please configure Reddit API credentials.")

    def _mock_texts(self) -> List[str]:
        return [
            "Feeling great about the new project! Excited to see where this goes.",
            "Stressed about the deadline tomorrow. Need to finish everything.",
            "Beautiful weather today. Perfect for a walk in the park.",
            "Anxious about the upcoming exam. Hope I studied enough.",
            "Just got promoted! This is amazing news!",
            "Traffic is terrible today. Going to be late for the meeting.",
            "Love spending time with family. These moments are precious.",
            "Worried about climate change. We need to act now.",
            "Grateful for all the support from friends and colleagues.",
            "Frustrated with the slow internet connection.",
            "Celebrating a small victory today. Every step counts!",
            "Feeling overwhelmed with all the tasks on my plate.",
            "Amazing sunset tonight. Nature never fails to amaze.",
            "Concerned about the future. Hoping for the best.",
            "Thrilled about the concert next week! Can't wait!",
        ]

    async def fetch_city_posts(self, city: str, limit: int = 50) -> List[Dict]:
        """
        Fetch recent posts mentioning the city from Reddit. Returns list of dicts:
        { platform, text, url, author, lat, lng }
        """
        results: List[Dict] = []
        
        if not self.reddit_client:
            raise Exception("Reddit API not configured. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")
        
        try:
            # Search Reddit for posts mentioning the city
            query = f'"{city}" (feeling OR mood OR today OR life OR community OR people OR weather OR living OR resident)'
            
            print(f"Searching Reddit for: {query}")
            
            for submission in self.reddit_client.subreddit("all").search(
                query=query,
                limit=limit * 2,  # Fetch more to filter out short posts
                sort="new",
                time_filter="week"  # Last week to get more results
            ):
                text = submission.title
                if hasattr(submission, 'selftext') and submission.selftext:
                    text += " " + (submission.selftext or "")
                text = (text or "").strip()
                
                # Skip very short posts or posts without meaningful content
                if not text or len(text) < 20:
                    continue
                
                # Get post URL
                url = f"https://reddit.com{submission.permalink}" if hasattr(submission, 'permalink') else None
                author = submission.author.name if hasattr(submission, 'author') and submission.author else "unknown"
                
                results.append({
                    "platform": "reddit",
                    "text": text[:1000],  # Limit text length
                    "url": url,
                    "author": author,
                    "lat": 0.0,  # Will be filled by caller if needed
                    "lng": 0.0
                })
                
                if len(results) >= limit:
                    break
            
            print(f"Found {len(results)} real Reddit posts for {city}")
                    
        except Exception as e:
            print(f"Error fetching city posts from Reddit: {e}")
            raise Exception(f"Failed to fetch Reddit posts: {str(e)}")
        
        if not results:
            raise Exception(f"No Reddit posts found for {city}. Try a different city or check Reddit API credentials.")
        
        return results

