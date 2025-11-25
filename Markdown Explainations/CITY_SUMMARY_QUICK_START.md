# Quick Start: City Summary Feature

## Prerequisites

Before using the city summary feature, ensure you have the following API keys configured:

### Required
- **Reddit API** credentials (for fetching city posts)

### Optional (for enhanced features)
- **OpenRouter API** key (for AI-generated summaries)
- **ElevenLabs API** key (for audio narration)

## Setup Instructions

### 1. Configure Backend Environment

Create or update `backend/.env` with your API credentials:

```bash
# Reddit API - REQUIRED
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=EarthPulse/1.0

# OpenRouter API - OPTIONAL (for AI summaries)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openrouter/llama-3.1-8b-instruct:free

# ElevenLabs API - OPTIONAL (for audio narration)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### 2. Get API Keys

#### Reddit API (Required)
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" type
4. Fill in name, description, and redirect URI (use http://localhost:8000)
5. Copy the client ID and secret

#### OpenRouter API (Optional)
1. Go to https://openrouter.ai/
2. Sign up or log in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key

#### ElevenLabs API (Optional)
1. Go to https://elevenlabs.io/
2. Sign up for a free account
3. Go to Profile → API Keys
4. Generate a new API key
5. Copy the key

### 3. Start the Application

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Using the Feature

### Step 1: Select a City

1. Open the application in your browser (http://localhost:3000)
2. Wait for the globe to load with city data points
3. Click on any colored point on the globe
4. A popup card will appear showing basic sentiment info

### Step 2: Generate City Summary

1. In the popup card, click the **"🤖 Generate AI Summary"** button
2. A modal will open and automatically start fetching data
3. Wait for the analysis to complete (usually 5-10 seconds)
4. Review the summary information:
   - **Statistics**: Total posts, positive/neutral/negative counts
   - **Sentiment Meter**: Visual representation of average score
   - **AI Summary**: Natural language description of the city's mood
   - **Sample Posts**: Example posts with sentiment labels

### Step 3: Generate Audio (Optional)

1. In the summary modal, click **"🎙️ Generate Audio Summary"**
2. Wait for audio generation (5-15 seconds)
3. Audio will automatically play when ready
4. Click **"🔊 Play Again"** to replay the audio

## Troubleshooting

### No Posts Found
**Problem**: Modal shows "No posts found for city"

**Solutions**:
- Verify Reddit API credentials are correct
- Try a different, larger city
- Check that the Reddit app is approved (not banned)

### Slow Response
**Problem**: Summary takes a long time to load

**Solutions**:
- Reddit API may be slow - be patient
- Try reducing the limit parameter in the API call
- Check your internet connection

### Audio Generation Failed
**Problem**: "ElevenLabs API key not configured" or audio fails

**Solutions**:
- Add `ELEVENLABS_API_KEY` to backend `.env`
- Restart the backend server
- Check ElevenLabs account quota (free tier: 10k chars/month)
- Verify API key has correct permissions

### No AI Summary (Fallback Text)
**Problem**: Summary looks generic/rule-based

**Solutions**:
- Add `OPENROUTER_API_KEY` to enable AI summaries
- Check OpenRouter account has available credits
- Verify API key is valid

## Feature Limitations

### Free Tier Limits
- **Reddit**: 60 requests/minute
- **OpenRouter**: Varies by model (some models are free)
- **ElevenLabs**: 10,000 characters/month (free tier)

### Data Freshness
- Fetches posts from the last week
- Cache duration: 45 seconds
- May not reflect real-time events immediately

### City Coverage
- Works best with major cities (more Reddit posts)
- Smaller cities may have limited data
- City name must match Reddit search terms

## Tips for Best Results

1. **Choose Popular Cities**: Toronto, London, Tokyo, New York have more data
2. **Wait Between Requests**: Respect API rate limits
3. **Try Different Times**: Posts vary by time of day and day of week
4. **Check Sample Posts**: Verify the posts are relevant to the city
5. **Multiple Summaries**: Generate summaries for different cities to compare

## Next Steps

- Explore different cities around the globe
- Compare sentiment between cities
- Try generating audio in different voices (if ElevenLabs configured)
- Check out the full documentation in `CITY_SUMMARY_FEATURE.md`

## Support

For issues or questions:
- Check `CITY_SUMMARY_FEATURE.md` for detailed documentation
- Review API provider documentation
- Check browser console for error messages
- Verify environment variables are set correctly
