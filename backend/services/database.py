"""
Database Service
Handles MongoDB operations for storing and retrieving mood data
"""

import os
from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from models.mood import MoodPoint
from models.post import PostItem

load_dotenv()

class DatabaseService:
    """MongoDB service for mood data storage"""
    
    def __init__(self, uri: Optional[str] = None):
        self.client = None
        self.db = None
        self.collection = None
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/earthpulse")
        self.db_name = "earthpulse"
        self.collection_name = "moods"
        self._posts_mem: List[dict] = []  # in-memory fallback
        # If using Mongo, ensure 'posts' collection exists with indexes
        if self.client:
            self.posts = self.db.get_collection("posts")
            try:
                self.posts.create_index([("city_name", 1), ("created_at", -1)])
            except Exception:
                pass
    
    async def connect(self):
        """Connect to MongoDB"""
        # Log which MongoDB URI is being used and whether it's local or cloud
        if self.mongodb_uri.startswith("mongodb://localhost"):
            print(f"🌐 Attempting to connect to LOCAL MongoDB at: {self.mongodb_uri}")
        elif self.mongodb_uri.startswith("mongodb+srv://"):
            print(f"☁️ Attempting to connect to CLOUD MongoDB Atlas at: {self.mongodb_uri}")
        else:
            print(f"🌐 Attempting to connect to MongoDB at: {self.mongodb_uri}")

        try:
            self.client = AsyncIOMotorClient(self.mongodb_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            # Test connection
            await self.client.admin.command('ping')
            print("✅ Connected to MongoDB")
            
            # Create indexes for better query performance
            await self.collection.create_index([("timestamp", -1)])  # Descending timestamp
            await self.collection.create_index([("lat", 1), ("lng", 1)])  # Location index
            await self.collection.create_index([("source", 1)])  # Source index
            
        except ConnectionFailure as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            print("⚠️ Using in-memory storage (data will be lost on restart)")
            self.client = None
        except Exception as e:
            print(f"⚠️ Error connecting to MongoDB: {e}")
            self.client = None
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")
    
    async def check_connection(self) -> bool:
        """Check if database connection is active"""
        if not self.client:
            return False
        try:
            await self.client.admin.command('ping')
            return True
        except:
            return False
    
    async def insert_moods(self, moods: List[MoodPoint]):
        """Insert mood points into database"""
        if not self.client:
            # In-memory storage fallback
            if not hasattr(self, '_in_memory_storage'):
                self._in_memory_storage = []
            self._in_memory_storage.extend([mood.dict() for mood in moods])
            # Keep only last 1000 items in memory
            self._in_memory_storage = self._in_memory_storage[-1000:]
            return
        
        try:
            documents = [mood.dict() for mood in moods]
            # Convert datetime to proper format
            for doc in documents:
                if doc.get("timestamp") and isinstance(doc["timestamp"], datetime):
                    doc["timestamp"] = doc["timestamp"]
            
            result = await self.collection.insert_many(documents)
            print(f"✅ Inserted {len(result.inserted_ids)} mood points")
        except Exception as e:
            print(f"Error inserting moods: {e}")
    
    async def get_moods(
        self,
        limit: int = 100,
        source: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        hours: Optional[int] = 24
    ) -> List[MoodPoint]:
        """
        Retrieve mood points from database
        
        Args:
            limit: Maximum number of points to return
            source: Filter by source ('reddit' or 'twitter')
            min_score: Minimum sentiment score
            max_score: Maximum sentiment score
            hours: Only return data from last N hours
        """
        if not self.client:
            # Return in-memory data
            if not hasattr(self, '_in_memory_storage'):
                return []
            
            moods = self._in_memory_storage.copy()
            
            # Apply filters
            if source:
                moods = [m for m in moods if m.get("source") == source]
            if min_score is not None:
                moods = [m for m in moods if m.get("score", 0) >= min_score]
            if max_score is not None:
                moods = [m for m in moods if m.get("score", 0) <= max_score]
            if hours:
                cutoff = datetime.utcnow() - timedelta(hours=hours)
                moods = [m for m in moods if m.get("timestamp", datetime.utcnow()) >= cutoff]
            
            # Sort by timestamp (newest first) and limit
            moods.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
            return [MoodPoint(**m) for m in moods[:limit]]
        
        try:
            # Build query
            query = {}
            
            if source:
                query["source"] = source
            
            if min_score is not None or max_score is not None:
                query["score"] = {}
                if min_score is not None:
                    query["score"]["$gte"] = min_score
                if max_score is not None:
                    query["score"]["$lte"] = max_score
            
            if hours:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                query["timestamp"] = {"$gte": cutoff_time}
            
            # Execute query
            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
            moods = await cursor.to_list(length=limit)
            
            # Convert to MoodPoint objects
            return [MoodPoint(**mood) for mood in moods]
        except Exception as e:
            print(f"Error fetching moods: {e}")
            return []
    
    async def get_statistics(self) -> Dict:
        """Get statistics about stored mood data"""
        if not self.client:
            if not hasattr(self, '_in_memory_storage'):
                return {
                    "total_points": 0,
                    "by_source": {},
                    "by_label": {},
                    "average_score": 0.0
                }
            
            moods = self._in_memory_storage
            
            stats = {
                "total_points": len(moods),
                "by_source": {},
                "by_label": {},
                "average_score": 0.0
            }
            
            scores = []
            for mood in moods:
                source = mood.get("source", "unknown")
                label = mood.get("label", "unknown")
                score = mood.get("score", 0)
                
                stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
                stats["by_label"][label] = stats["by_label"].get(label, 0) + 1
                scores.append(score)
            
            if scores:
                stats["average_score"] = sum(scores) / len(scores)
            
            return stats
        
        try:
            total = await self.collection.count_documents({})
            
            # Aggregate by source
            source_pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}}}
            ]
            source_results = await self.collection.aggregate(source_pipeline).to_list(length=10)
            by_source = {r["_id"]: r["count"] for r in source_results}
            
            # Aggregate by label
            label_pipeline = [
                {"$group": {"_id": "$label", "count": {"$sum": 1}}}
            ]
            label_results = await self.collection.aggregate(label_pipeline).to_list(length=10)
            by_label = {r["_id"]: r["count"] for r in label_results}
            
            # Average score
            avg_pipeline = [
                {"$group": {"_id": None, "avg": {"$avg": "$score"}}}
            ]
            avg_result = await self.collection.aggregate(avg_pipeline).to_list(length=1)
            avg_score = avg_result[0]["avg"] if avg_result else 0.0
            
            return {
                "total_points": total,
                "by_source": by_source,
                "by_label": by_label,
                "average_score": round(avg_score, 3)
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                "total_points": 0,
                "by_source": {},
                "by_label": {},
                "average_score": 0.0
            }
    
    async def insert_posts(self, posts: List[PostItem]) -> int:
        """Insert posts into database"""
        docs = [p.dict() for p in posts]
        if getattr(self, "posts", None):
            await self.posts.insert_many(docs)
            return len(docs)
        self._posts_mem.extend(docs)
        return len(docs)

    async def get_posts_by_city(self, city: str, limit: int = 50) -> List[dict]:
        """Get posts for a specific city"""
        if getattr(self, "posts", None):
            cursor = self.posts.find({"city_name": city}).sort("created_at", -1).limit(limit)
            return [doc async for doc in cursor]
        # memory
        res = [p for p in self._posts_mem if p.get("city_name") == city]
        res.sort(key=lambda x: x.get("created_at"), reverse=True)
        return res[:limit]

