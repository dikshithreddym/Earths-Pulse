# City Summary Feature Documentation

## Overview

The City Summary Feature enables users to generate real-time, AI-powered sentiment summaries for specific cities using Reddit API data. Users can click on any city pointer on the globe to view detailed sentiment analysis and generate audio narration using ElevenLabs Text-to-Speech.

## Features

### 1. **Interactive City Selection**
- Click on any city pointer on the globe to view basic sentiment information
- A popup card displays:
  - City name
  - Current sentiment (Positive/Neutral/Negative)
  - Emotion label
  - Sentiment score
  - Data source

### 2. **AI-Powered City Summary**
- Click the "🤖 Generate AI Summary" button on the city card
- Opens a detailed modal with:
  - **Statistics Dashboard**: Total posts analyzed, positive/neutral/negative distribution
  - **Visual Sentiment Meter**: Bar chart showing average sentiment score
  - **AI-Generated Summary**: Natural language description of the city's emotional climate
  - **Sample Posts**: Up to 5 example posts with sentiment labels
  - **Real-time Data**: Fetched directly from Reddit API

### 3. **Audio Narration**
- Click "🎙️ Generate Audio Summary" to convert the text summary to speech
- Uses ElevenLabs API for high-quality voice synthesis
- Audio auto-plays when generated
- Can replay audio with "🔊 Play Again" button
- Supports multiple ElevenLabs voices and models

## Backend Implementation

### New API Endpoints

#### 1. `GET /api/city/summary`
Generates AI-powered sentiment summary for a specific city.

**Query Parameters:**
- `city` (required): Name of the city to analyze
- `limit` (optional, default: 50): Number of posts to fetch and analyze

**Response:**
```json
{
  "city": "Toronto",
  "summary": "AI-generated summary text...",
  "statistics": {
    "total_posts": 50,
    "positive": 25,
    "neutral": 15,
    "negative": 10,
    "average_score": 0.245
  },
  "sample_posts": [
    {
      "text": "Post content...",
      "platform": "reddit",
      "score": 0.8,
      "label": "joy"
    }
  ],
  "timestamp": "2025-11-09T12:34:56.789Z"
}
```

**Error Responses:**
- `404`: No posts found for the city
- `500`: Error during analysis or summary generation

#### 2. `GET /api/city/summary/audio`
Converts city summary to audio narration using ElevenLabs.

**Query Parameters:**
- `city` (required): Name of the city
- `limit` (optional, default: 50): Number of posts to analyze
- `format` (optional, default: "base64"): Output format ("base64", "url", or "stream")
- `voice_id` (optional): ElevenLabs voice ID or name
- `model` (optional): ElevenLabs model to use

**Response (format=base64):**
```json
{
  "audio_base64": "base64_encoded_audio_data...",
  "mime": "audio/mpeg",
  "summary": "The summary text that was narrated...",
  "city": "Toronto",
  "statistics": { ... },
  "timestamp": "2025-11-09T12:34:56.789Z"
}
```

**Error Responses:**
- `400`: ElevenLabs API key not configured
- `404`: City not found or no posts available
- `500`: Error during audio generation

### Backend Files Modified

1. **`backend/main.py`**
   - Added `get_city_summary()` endpoint
   - Added `get_city_summary_audio()` endpoint

2. **`backend/services/summary_generator.py`**
   - Updated `generate_summary()` to accept optional `city_name` parameter
   - Updated `_generate_fallback_summary()` for city-specific summaries
   - Updated `_build_prompt()` for city-focused AI prompts
   - Added `_generate_ai_summary()` method for OpenRouter integration

3. **`backend/services/social_fetcher.py`**
   - Enhanced `fetch_city_posts()` to actually fetch Reddit posts for specific cities
   - Added proper error handling and fallback mechanisms
   - Improved Reddit search with better queries

## Frontend Implementation

### New Components

#### 1. **CitySummaryModal.tsx**
A comprehensive modal component that displays city sentiment analysis.

**Key Features:**
- Fetches city summary data on open
- Displays statistics with color-coded cards
- Shows visual sentiment meter
- Generates and plays audio narration
- Handles loading, error, and success states
- Responsive design for mobile and desktop

**Props:**
```typescript
interface CitySummaryModalProps {
  open: boolean
  city?: string
  onClose: () => void
  apiBaseUrl: string
}
```

### Frontend Files Modified

1. **`frontend/components/CitySummaryModal.tsx`** (NEW)
   - Full-featured modal for city summary display
   - Audio generation and playback functionality
   - Statistics visualization
   - Error handling UI

2. **`frontend/components/Globe.tsx`**
   - Added `onGenerateSummary` prop
   - Enhanced point card popup with "Generate AI Summary" button
   - Button click triggers city summary modal

3. **`frontend/app/page.tsx`**
   - Integrated `CitySummaryModal` component
   - Added `handleGenerateSummary()` function
   - State management for summary modal

## Setup Requirements

### Backend

1. **Reddit API Credentials** (Required for real city data)
   - Set `REDDIT_CLIENT_ID` in `.env`
   - Set `REDDIT_CLIENT_SECRET` in `.env`
   - Set `REDDIT_USER_AGENT` in `.env`

2. **OpenRouter API** (Optional - for AI summaries)
   - Set `OPENROUTER_API_KEY` in `.env`
   - Set `OPENROUTER_MODEL` (optional) for specific model

3. **ElevenLabs API** (Optional - for audio generation)
   - Set `ELEVENLABS_API_KEY` in `.env`
   - Set `ELEVENLABS_VOICE_ID` (optional) for specific voice

### Environment Variables

Add to `backend/.env`:
```bash
# Reddit API (Required for city summaries)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=EarthPulse/1.0

# OpenRouter API (Optional - for AI summaries)
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=openrouter/llama-3.1-8b-instruct:free

# ElevenLabs API (Optional - for audio narration)
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

## Usage Flow

1. **User clicks on a city point** on the globe
   - Globe displays city information card
   - Card shows current sentiment and emotion

2. **User clicks "🤖 Generate AI Summary"**
   - Frontend opens `CitySummaryModal`
   - Modal fetches city summary from `/api/city/summary`
   - Backend:
     - Fetches recent Reddit posts about the city
     - Analyzes sentiment for each post
     - Generates AI-powered summary (if OpenRouter configured)
     - Returns statistics and sample posts

3. **User clicks "🎙️ Generate Audio Summary"**
   - Frontend requests audio from `/api/city/summary/audio`
   - Backend:
     - Uses existing summary data
     - Calls ElevenLabs API to synthesize speech
     - Returns audio as base64 or URL
   - Frontend:
     - Converts base64 to blob
     - Creates audio element
     - Auto-plays the narration

## Technical Details

### Sentiment Analysis
- Uses transformer-based models for accurate sentiment detection
- Scores range from -1.0 (very negative) to +1.0 (very positive)
- Thresholds: Positive > 0.3, Negative < -0.3, Neutral between

### Reddit Data Fetching
- Searches r/all with city-specific queries
- Filters posts from the last week for relevance
- Combines post title and body text for analysis
- Limits to 50 posts per city (configurable)

### AI Summary Generation
- Uses OpenRouter API with LLaMA or similar models
- Fallback to rule-based summaries if API unavailable
- Focuses on emotional climate and sentiment trends
- Concise, narrative style (3-5 sentences)

### Audio Generation
- ElevenLabs Text-to-Speech API
- Supports multiple voices and models
- MP3 format output
- Base64 encoding for easy frontend consumption

## Error Handling

### Backend
- **No Reddit API**: Returns mock data with clear indication
- **No OpenRouter API**: Falls back to rule-based summaries
- **No ElevenLabs API**: Returns 400 error with clear message
- **City not found**: Returns 404 with helpful error message
- **API failures**: Proper error propagation with status codes

### Frontend
- **Network errors**: Displays error message in modal
- **No data**: Shows "No posts captured" message
- **Audio failures**: Displays error and allows retry
- **Loading states**: Shows spinners with descriptive text

## Performance Considerations

1. **Caching**: Summary generator includes 45-second cache TTL
2. **Rate Limiting**: Reddit API calls are controlled per city
3. **Lazy Loading**: Summary only fetched when modal opens
4. **Audio Optimization**: Base64 encoding for smaller payloads
5. **Responsive Design**: Works on mobile and desktop

## Future Enhancements

1. **Historical Trends**: Show sentiment changes over time
2. **Comparison View**: Compare multiple cities side-by-side
3. **Export Options**: Download summaries as PDF or share links
4. **Custom Date Ranges**: Allow users to select time periods
5. **More Data Sources**: Integrate Twitter, news APIs, etc.
6. **Voice Selection**: Allow users to choose TTS voice in UI
7. **Language Support**: Multi-language summaries and TTS

## Testing

### Manual Testing Steps

1. **Test City Summary Generation**
   ```bash
   curl "http://localhost:8000/api/city/summary?city=Toronto&limit=50"
   ```

2. **Test Audio Generation**
   ```bash
   curl "http://localhost:8000/api/city/summary/audio?city=Toronto&format=base64"
   ```

3. **Test Frontend Integration**
   - Start both backend and frontend
   - Click on a city point on the globe
   - Click "Generate AI Summary" button
   - Verify modal opens with data
   - Click "Generate Audio Summary"
   - Verify audio plays

## Troubleshooting

### "No posts found for city"
- Check Reddit API credentials
- Verify city name spelling
- Try a major city first (e.g., Toronto, London, Tokyo)

### "ElevenLabs API key not configured"
- Add `ELEVENLABS_API_KEY` to backend `.env`
- Restart the backend server

### Audio doesn't play
- Check browser console for errors
- Verify audio format is supported (MP3)
- Check ElevenLabs API quota/limits

### Slow response times
- Reddit API may be slow for some searches
- Reduce `limit` parameter (default 50)
- Check network connection

## API Rate Limits

- **Reddit**: ~60 requests per minute (with OAuth)
- **OpenRouter**: Varies by model (free tier available)
- **ElevenLabs**: 10,000 characters/month (free tier)

## Credits

- **Sentiment Analysis**: HuggingFace Transformers
- **AI Summaries**: OpenRouter API
- **Text-to-Speech**: ElevenLabs API
- **Social Data**: Reddit API (PRAW)
