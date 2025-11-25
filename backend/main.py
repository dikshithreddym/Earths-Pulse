"""
FastAPI Backend for Earth's Pulse
Main application entry point with API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional
import asyncio
import base64
from io import BytesIO
from uuid import uuid4
from pathlib import Path
import logging
import httpx

from services.sentiment_analyzer import SentimentAnalyzer
from services.social_fetcher import SocialMediaFetcher
from services.database import DatabaseService
from services.summary_generator import SummaryGenerator
from models.mood import MoodPoint
from models.post import PostItem
from utils.geo import nearest_city
from data.cities_200 import CITIES_200
import random
from services.tts import tts_service, ElevenLabsError

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Earth's Pulse API",
    description="Real-time emotional sentiment analysis from social media",
    version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://earthspulse.vercel.app",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
        # Add your custom domain here when you have one
        # "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for serving generated audio when format=url
STATIC_DIR = Path(__file__).parent / "static"
AUDIO_DIR = STATIC_DIR / "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize services
sentiment_analyzer = SentimentAnalyzer()
social_fetcher = SocialMediaFetcher()
db_service = DatabaseService()
summary_generator = SummaryGenerator()
background_task_handle = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await db_service.connect()
    print("✅ Backend services initialized")

    # Start background refresh task (Reddit-only, city-specific) if enabled
    try:
        enable_bg = os.getenv("ENABLE_BACKGROUND_REFRESH", "true").lower() == "true"
        interval_min = int(os.getenv("REFRESH_INTERVAL_MINUTES", "60"))
        if enable_bg and interval_min > 0:
            async def _background_refresh_loop():
                while True:
                    try:
                        # Fetch one post per city (Reddit-only)
                        posts = await social_fetcher.fetch_reddit_city_posts(CITIES_200, per_city=1)

                        mood_points = []
                        for post in posts:
                            try:
                                sentiment_result = sentiment_analyzer.analyze(post["text"])
                                mood = MoodPoint(
                                    lat=post["lat"],
                                    lng=post["lng"],
                                    label=sentiment_result["label"],
                                    score=sentiment_result["score"],
                                    source="reddit",
                                    text=post["text"][:200],
                                    city_name=post.get("city_name"),
                                    timestamp=datetime.utcnow(),
                                    is_fallback=post.get("is_fallback", False),
                                )
                                mood_points.append(mood)
                            except Exception as e:
                                print(f"Background analyze error: {e}")
                        if mood_points:
                            await db_service.insert_moods(mood_points)
                            print(f"🟢 Background refresh: inserted {len(mood_points)} points")
                    except Exception as e:
                        print(f"Background refresh error: {e}")

                    await asyncio.sleep(max(60, interval_min * 60))

            global background_task_handle
            background_task_handle = asyncio.create_task(_background_refresh_loop())
            print(f"🕒 Background refresh enabled (every {interval_min} min)")
    except Exception as e:
        print(f"Failed to start background refresh: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db_service.disconnect()
    print("✅ Backend services shut down")
    global background_task_handle
    if background_task_handle:
        background_task_handle.cancel()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🌍 Earth's Pulse API",
        "version": "1.0.0",
        "endpoints": {
            "moods": "/api/moods",
            "summary": "/api/summary",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": await db_service.check_connection(),
            "sentiment_analyzer": sentiment_analyzer.is_ready(),
            "social_fetcher": social_fetcher.is_ready()
        }
    }


@app.get("/api/moods", response_model=List[MoodPoint])
async def get_moods(
    limit: Optional[int] = 100,
    source: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    only_city: Optional[bool] = False,
    unique_per_city: Optional[bool] = False):
    """
    Get mood data points from database
    
    Query parameters:
    - limit: Maximum number of points to return (default: 100)
    - source: Filter by source ('reddit' or 'twitter')
    - min_score: Minimum sentiment score (-1 to 1)
    - max_score: Maximum sentiment score (-1 to 1)
    """
    try:
        moods = await db_service.get_moods(
            limit=limit,
            source=source,
            min_score=min_score,
            max_score=max_score
        )

        # Optionally filter to only records that have a city_name
        if only_city:
            moods = [m for m in moods if getattr(m, "city_name", None)]

        # Optionally dedupe so we return at most one (latest) per city
        if unique_per_city:
            seen = set()
            unique: List[MoodPoint] = []
            for m in moods:
                name = getattr(m, "city_name", None)
                if not name:
                    continue
                if name not in seen:
                    unique.append(m)
                    seen.add(name)
            moods = unique

        return moods
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching moods: {str(e)}")


@app.post("/api/moods/refresh")
async def refresh_moods(mode: Optional[str] = "city", reddit_only: bool = True):
    """
    Manually trigger data refresh from social media APIs
    Fetches new posts, analyzes sentiment, and stores in database
    """
    try:
        # Fetch posts from social media
        if mode == "city":
            # One post per curated city (Reddit-only)
            posts = await social_fetcher.fetch_reddit_city_posts(CITIES_200, per_city=1)
        else:
            posts = await social_fetcher.fetch_recent_posts(limit=50, reddit_only=reddit_only)
        
        if not posts:
            return {
                "message": "No new posts fetched",
                "count": 0
            }
        
        # Analyze sentiment for each post
        mood_points = []
        for post in posts:
            try:
                sentiment_result = sentiment_analyzer.analyze(post["text"])
                
                mood_point = MoodPoint(
                    lat=post["lat"],
                    lng=post["lng"],
                    label=sentiment_result["label"],
                    score=sentiment_result["score"],
                    source=post.get("source", "reddit"),
                    text=post["text"][:200],  # Truncate for storage
                    city_name=post.get("city_name"),
                    timestamp=datetime.utcnow(),
                    is_fallback=post.get("is_fallback", False)
                )
                
                mood_points.append(mood_point)
            except Exception as e:
                print(f"Error analyzing post: {e}")
                continue
        
        # Store in database
        if mood_points:
            await db_service.insert_moods(mood_points)
        
        return {
            "message": "Moods refreshed successfully",
            "count": len(mood_points),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing moods: {str(e)}")


@app.get("/api/summary")
async def get_summary():
    try:
        recent_moods = await db_service.get_moods(limit=500)
        if not recent_moods:
            return {
                "summary": "No mood data available yet. Please refresh the data.",
                "timestamp": datetime.utcnow().isoformat()
            }
        # Keep latest per city (assuming recent_moods already sorted newest first)
        unique_by_city = {}
        for m in recent_moods:
            city = getattr(m, "city_name", None)
            if city and city not in unique_by_city:
                unique_by_city[city] = m
        deduped = list(unique_by_city.values())
        summary = await summary_generator.generate_summary(deduped)
        return {
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
            "data_points": len(deduped),
            "raw_points_scanned": len(recent_moods)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@app.get("/api/summary/audio")
async def get_summary_audio(
    format: Optional[str] = "base64",
    voice_id: Optional[str] = None,
    model: Optional[str] = None):
    """
    Convert the AI-generated summary to speech using ElevenLabs.

    Query params:
    - format: 'base64' (default) | 'url' | 'stream'
    - voice_id: optional ElevenLabs voice id or name override
    """
    try:
        # Reuse dedupe logic so audio matches /api/summary output
        recent_moods = await db_service.get_moods(limit=500)
        if not recent_moods:
            raise HTTPException(status_code=400, detail="No mood data available yet.")

        unique_by_city = {}
        for m in recent_moods:
            city = getattr(m, "city_name", None)
            if city and city not in unique_by_city:
                unique_by_city[city] = m
        deduped = list(unique_by_city.values())

        summary_text = await summary_generator.generate_summary(deduped)

        if not tts_service.is_configured:
            raise HTTPException(status_code=400, detail="ElevenLabs API key not configured.")
        try:
            audio_bytes = await tts_service.synthesize(summary_text, voice=voice_id, model=model)
        except ElevenLabsError as e:
            raise HTTPException(status_code=e.status_code, detail=e.to_dict())

        fmt = (format or "base64").lower()
        if fmt == "stream":
            return StreamingResponse(BytesIO(audio_bytes), media_type="audio/mpeg")
        elif fmt == "url":
            filename = f"summary_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}.mp3"
            file_path = AUDIO_DIR / filename
            with open(file_path, "wb") as f:
                f.write(audio_bytes)
            return {
                "url": f"/static/audio/{filename}",
                "mime": "audio/mpeg",
                "summary": summary_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:  # base64
            b64 = base64.b64encode(audio_bytes).decode("ascii")
            return {
                "audio_base64": b64,
                "mime": "audio/mpeg",
                "summary": summary_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, ElevenLabsError):
            # Return a flattened error object (no double 'detail' nesting)
            raise HTTPException(status_code=getattr(e, "status_code", 500), detail=e.to_dict())
        raise HTTPException(status_code=500, detail=f"Error generating summary audio: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Get statistics about mood data"""
    try:
        stats = await db_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@app.post("/api/dev/seed")
async def dev_seed(force_clear: bool = False):
    """Development helper: seed the curated cities into the running server's database.

    This endpoint is intentionally development-only. It will insert one MoodPoint per city
    from `backend/data/cities_100.py` using the server's `db_service` and `sentiment_analyzer`.
    """
    # Only allow in development environment for safety
    if os.getenv("ENVIRONMENT", "development") != "development":
        raise HTTPException(status_code=403, detail="Seeding only allowed in development environment")

    try:
        if force_clear:
            # Clear existing data
            if db_service.client and db_service.collection:
                await db_service.collection.delete_many({})
            else:
                db_service._in_memory_storage = []

        sample_texts = [
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
        ]

        mood_points = []
        for city in CITIES_200:
            text = random.choice(sample_texts)
            source = random.choice(["reddit", "twitter"])
            result = sentiment_analyzer.analyze(text)

            mood = MoodPoint(
                lat=city["lat"],
                lng=city["lng"],
                label=result["label"],
                score=result["score"],
                source=source,
                text=f"{text} — seeded for {city['name']}",
                city_name=city["name"],
                timestamp=datetime.utcnow(),
                is_fallback=True,
            )
            mood_points.append(mood)

        if mood_points:
            await db_service.insert_moods(mood_points)

        stats = await db_service.get_statistics()
        return {"message": "Seeded curated cities", "inserted": len(mood_points), "stats": stats}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeding data: {e}")


@app.post("/api/dev/clear")
async def dev_clear():
    """Development helper: clear all mood data from the server (DB or in-memory)."""
    if os.getenv("ENVIRONMENT", "development") != "development":
        raise HTTPException(status_code=403, detail="Clearing only allowed in development environment")

    try:
        if db_service.client and db_service.collection:
            await db_service.collection.delete_many({})
        else:
            db_service._in_memory_storage = []
        return {"message": "Cleared mood data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {e}")


@app.get("/api/openrouter/health")
async def openrouter_health():
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise HTTPException(status_code=400, detail="OPENROUTER_API_KEY not set")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {key}"}
            )
        if r.status_code != 200:
            return JSONResponse(status_code=r.status_code, content={
                "ok": False,
                "status": r.status_code,
                "error": r.text
            })
        data = r.json()
        return {
            "ok": True,
            "status": 200,
            "models_available": len(data.get("data", [])),
            "sample_models": [m.get("id") for m in data.get("data", [])[:5]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


def _clean_openrouter_text(txt: str) -> str:
    if not txt:
        return ""
    junk = ["<s>", "</s>", "[/s]", "[/S]", "</S>"]
    for j in junk:
        txt = txt.replace(j, "")
    return txt.strip()

@app.get("/api/openrouter/test")
async def openrouter_test(
    prompt: Optional[str] = "Say 'pong'.",
    model: Optional[str] = None):
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise HTTPException(status_code=400, detail="OPENROUTER_API_KEY not set")

    # Force a minimal safe prompt if user passed empty
    user_prompt = prompt.strip() if prompt else "Say 'pong'."

    fallback_models = [
        model or os.getenv("OPENROUTER_MODEL", "").strip(),
        "openrouter/llama-3.1-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ]
    models_to_try = [m for m in dict.fromkeys(fallback_models) if m]

    last_error = None
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            for m in models_to_try:
                r = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "Earth's Pulse"
                    },
                    json={
                        "model": m,
                        "messages": [
                            {"role": "system", "content": "Return only the direct answer."},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": 60,
                        "temperature": 0.2,
                        "stop": ["</s>", "[/s]"]
                    }
                )
                if r.status_code == 200:
                    data = r.json()
                    raw = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
                    cleaned = _clean_openrouter_text(raw)
                    return {
                        "ok": True,
                        "model_used": m,
                        "output": cleaned,
                        "raw_output": raw,
                        "usage": data.get("usage")
                    }
                last_error = {"status": r.status_code, "body": r.text}
        return JSONResponse(status_code=502, content={"ok": False, "error": last_error or "Unknown failure"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test call failed: {e}")

@app.get("/api/posts")
async def get_posts_by_city(city: Optional[str] = None, limit: int = 50, live: bool = False, save: bool = True):
    """
    Returns analyzed posts for the given city.
    - live=true forces a fresh fetch+analyze if DB has none
    - save=true stores fresh results for reuse
    """
    if not city:
        raise HTTPException(status_code=400, detail="city is required")

    posts = []
    try:
        if not live:
            posts = await db_service.get_posts_by_city(city, limit=limit)
        if not posts:
            raw = await social_fetcher.fetch_city_posts(city, limit=limit)
            analyzed: list[PostItem] = []
            for r in raw:
                text = r.get("text") or ""
                sc, lbl = sentiment_analyzer.analyze_text(text)
                analyzed.append(PostItem(
                    city_name=city,
                    country=None,
                    platform=r.get("platform") or "unknown",
                    text=text,
                    url=r.get("url"),
                    author=r.get("author"),
                    score=sc,
                    label=lbl
                ))
            if save and analyzed:
                await db_service.insert_posts(analyzed)
            posts = [p.dict() for p in analyzed]
        return {"city": city, "count": len(posts), "posts": posts[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {e}")

@app.get("/api/city/posts")
async def get_city_posts(city: str, limit: int = 40, live: bool = True):
    moods = await db_service.get_moods(limit=1000)
    posts = []
    for m in moods:
        if getattr(m, "city_name", None) == city and getattr(m, "post_text", None):
            posts.append({
                "platform": getattr(m, "platform", None),
                "text": m.post_text,
                "url": getattr(m, "post_url", None),
                "author": getattr(m, "post_author", None),
                "score": float(m.score),
                "label": m.label,
                "timestamp": getattr(m, "timestamp", None).isoformat() if getattr(m, "timestamp", None) else None
            })
            if len(posts) >= limit:
                break

    if not posts and live and hasattr(social_fetcher, "fetch_city_posts"):
        raw = await social_fetcher.fetch_city_posts(city, limit=limit)
        for r in raw:
            text = r.get("text") or ""
            score, label = sentiment_analyzer.analyze_text(text)
            posts.append({
                "platform": r.get("platform") or "unknown",
                "text": text,
                "url": r.get("url"),
                "author": r.get("author"),
                "score": score,
                "label": label,
                "timestamp": datetime.utcnow().isoformat()
            })
            if len(posts) >= limit:
                break

    return {"city": city, "count": len(posts), "posts": posts[:limit]}

@app.get("/api/posts/near")
async def get_posts_near(lat: float, lng: float, limit: int = 50, within_km: float = 120):
    city = nearest_city(lat, lng, within_km=within_km)
    if not city:
        raise HTTPException(status_code=404, detail="No nearby city")
    return await get_city_posts(city=city["name"], limit=limit, live=True)


@app.get("/api/city/summary")
async def get_city_summary(city: str, limit: int = 50):
    """
    Generate an AI-powered summary of sentiment for a specific city
    using REAL Reddit posts and OpenRouter AI - NO MOCK DATA.
    
    Query parameters:
    - city: Name of the city to analyze
    - limit: Maximum number of posts to fetch (default: 50)
    """
    try:
        # Fetch REAL posts from Reddit API (no fallbacks)
        try:
            raw_posts = await social_fetcher.fetch_city_posts(city, limit=limit)
        except Exception as reddit_error:
            # If Reddit API fails, return clear error
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch Reddit posts for {city}: {str(reddit_error)}. Please check Reddit API credentials."
            )
        
        if not raw_posts:
            raise HTTPException(
                status_code=404, 
                detail=f"No Reddit posts found for {city}. The city might not have recent discussions on Reddit."
            )
        
        # Analyze sentiment for each post
        analyzed_posts = []
        mood_points = []
        
        for post in raw_posts:
            text = post.get("text", "")
            if not text:
                continue
                
            sentiment_result = sentiment_analyzer.analyze(text)
            
            analyzed_posts.append({
                "text": text[:300],
                "platform": post.get("platform", "reddit"),
                "score": sentiment_result["score"],
                "label": sentiment_result["label"],
                "url": post.get("url"),  # Include Reddit post URL
                "author": post.get("author")  # Include author name
            })
            
            # Create mood point for summary generation
            mood_point = MoodPoint(
                lat=post.get("lat", 0.0),
                lng=post.get("lng", 0.0),
                label=sentiment_result["label"],
                score=sentiment_result["score"],
                source=post.get("platform", "reddit"),
                text=text[:200],
                city_name=city,
                timestamp=datetime.utcnow(),
            )
            mood_points.append(mood_point)
        
        if not mood_points:
            raise HTTPException(
                status_code=404,
                detail=f"Could not analyze posts for {city}"
            )
        
        # Generate REAL AI summary using OpenRouter (no fallbacks)
        try:
            summary_text = await summary_generator.generate_summary(mood_points, city_name=city)
        except Exception as ai_error:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to generate AI summary: {str(ai_error)}. Please check OpenRouter API key."
            )
        
        # Calculate statistics
        total = len(mood_points)
        positive = sum(1 for m in mood_points if m.score > 0.3)
        neutral = sum(1 for m in mood_points if -0.3 <= m.score <= 0.3)
        negative = sum(1 for m in mood_points if m.score < -0.3)
        avg_score = sum(m.score for m in mood_points) / total if total > 0 else 0
        
        return {
            "city": city,
            "summary": summary_text,
            "statistics": {
                "total_posts": total,
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
                "average_score": round(avg_score, 3)
            },
            "sample_posts": analyzed_posts[:5],  # Return top 5 posts as examples
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "reddit_api",  # Confirm real data
            "ai_model": "openrouter"  # Confirm AI-generated
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating city summary: {str(e)}")


@app.get("/api/city/summary/audio")
async def get_city_summary_audio(
    city: str,
    limit: int = 50,
    format: Optional[str] = "base64",
    voice_id: Optional[str] = None,
    model: Optional[str] = None):
    """
    Generate audio narration of the city summary using ElevenLabs.
    
    Query parameters:
    - city: Name of the city
    - limit: Number of posts to analyze (default: 50)
    - format: 'base64' (default) | 'url' | 'stream'
    - voice_id: Optional ElevenLabs voice id or name override
    - model: Optional ElevenLabs model override
    """
    try:
        # First get the city summary
        summary_data = await get_city_summary(city=city, limit=limit)
        summary_text = summary_data["summary"]
        
        if not tts_service.is_configured:
            raise HTTPException(
                status_code=400, 
                detail="ElevenLabs API key not configured. Please set ELEVENLABS_API_KEY in environment."
            )
        
        try:
            audio_bytes = await tts_service.synthesize(summary_text, voice=voice_id, model=model)
        except ElevenLabsError as e:
            raise HTTPException(status_code=e.status_code, detail=e.to_dict())
        
        fmt = (format or "base64").lower()
        
        if fmt == "stream":
            return StreamingResponse(BytesIO(audio_bytes), media_type="audio/mpeg")
        elif fmt == "url":
            filename = f"city_{city.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}.mp3"
            file_path = AUDIO_DIR / filename
            with open(file_path, "wb") as f:
                f.write(audio_bytes)
            return {
                "url": f"/static/audio/{filename}",
                "mime": "audio/mpeg",
                "summary": summary_text,
                "city": city,
                "statistics": summary_data["statistics"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:  # base64
            b64 = base64.b64encode(audio_bytes).decode("ascii")
            return {
                "audio_base64": b64,
                "mime": "audio/mpeg",
                "summary": summary_text,
                "city": city,
                "statistics": summary_data["statistics"],
                "timestamp": datetime.utcnow().isoformat(),
            }
            
    except HTTPException:
        raise
    except Exception as e:
        if isinstance(e, ElevenLabsError):
            raise HTTPException(status_code=getattr(e, "status_code", 500), detail=e.to_dict())
        raise HTTPException(status_code=500, detail=f"Error generating city summary audio: {str(e)}")


# Optional: allows `python main.py` for quick runs
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

