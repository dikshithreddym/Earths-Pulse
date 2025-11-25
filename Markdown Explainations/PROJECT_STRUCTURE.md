# 📁 Project Structure

```
Earth's Pulse/
│
├── README.md                 # Main project documentation
├── SETUP.md                  # Detailed setup instructions
├── PROJECT_STRUCTURE.md      # This file
├── docker-compose.yml        # Docker orchestration for full stack
│
├── backend/                  # FastAPI Python backend
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container definition
│   ├── .dockerignore       # Docker ignore patterns
│   ├── env.example         # Environment variables template
│   │
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   └── mood.py         # MoodPoint Pydantic model
│   │
│   └── services/           # Business logic services
│       ├── __init__.py
│       ├── sentiment_analyzer.py    # Hugging Face sentiment analysis
│       ├── social_fetcher.py        # Reddit/Twitter data fetching
│       ├── database.py              # MongoDB operations
│       └── summary_generator.py     # OpenRouter AI summaries
│
└── frontend/                # Next.js React frontend
    ├── package.json         # Node.js dependencies
    ├── next.config.js      # Next.js configuration
    ├── tsconfig.json       # TypeScript configuration
    ├── tailwind.config.js  # Tailwind CSS configuration
    ├── postcss.config.js   # PostCSS configuration
    ├── Dockerfile          # Frontend container definition
    ├── .gitignore         # Git ignore patterns
    ├── .env.example       # Environment variables template
    │
    ├── app/               # Next.js app directory
    │   ├── layout.tsx     # Root layout component
    │   ├── page.tsx       # Main page component
    │   └── globals.css    # Global styles
    │
    ├── components/        # React components
    │   ├── Globe.tsx      # 3D globe visualization
    │   ├── Sidebar.tsx    # Sidebar with stats and summary
    │   └── TrendChart.tsx # Plotly.js trend visualization
    │
    └── types/            # TypeScript type definitions
        └── mood.ts        # MoodPoint interface
```

## Key Files Explained

### Backend

- **main.py**: FastAPI application with all API endpoints
  - `/api/moods` - Get mood data points
  - `/api/moods/refresh` - Trigger data refresh
  - `/api/summary` - Get AI-generated summary
  - `/api/stats` - Get statistics
  - `/api/health` - Health check

- **services/sentiment_analyzer.py**: 
  - Uses `cardiffnlp/twitter-roberta-base-sentiment-latest` model
  - Analyzes text and returns sentiment label + score
  - Falls back to rule-based analysis if model unavailable

- **services/social_fetcher.py**:
  - Fetches posts from Reddit (PRAW) and Twitter (Tweepy)
  - Extracts location data (currently uses random locations for demo)
  - Generates mock data if APIs unavailable

- **services/database.py**:
  - MongoDB operations using Motor (async)
  - Falls back to in-memory storage if MongoDB unavailable
  - Handles CRUD operations for mood points

- **services/summary_generator.py**:
  - Uses OpenRouter API for AI summaries
  - Falls back to rule-based summaries if API unavailable
  - Analyzes regional emotional patterns

### Frontend

- **app/page.tsx**: 
  - Main page component
  - Fetches data from backend every 30 seconds
  - Renders Globe and Sidebar components

- **components/Globe.tsx**:
  - Uses `globe.gl` library (Three.js wrapper)
  - Displays 3D Earth with sentiment points
  - Color-coded points (green/yellow/red)
  - Interactive (rotate, zoom, hover tooltips)

- **components/Sidebar.tsx**:
  - Shows statistics and AI summary
  - Displays sentiment distribution
  - Includes trend chart

- **components/TrendChart.tsx**:
  - Uses Plotly.js for visualization
  - Shows sentiment trends over time
  - 24-hour rolling window

## Data Flow

1. **Data Collection**: 
   - Backend fetches posts from Reddit/Twitter
   - Or generates mock data if APIs unavailable

2. **Sentiment Analysis**:
   - Text is analyzed using Hugging Face model
   - Returns label (joyful/anxious/neutral) and score (-1 to 1)

3. **Storage**:
   - Mood points stored in MongoDB
   - Or in-memory if MongoDB unavailable

4. **API**:
   - Frontend requests data from `/api/moods`
   - Returns JSON array of mood points

5. **Visualization**:
   - Frontend renders points on 3D globe
   - Updates every 30 seconds
   - Sidebar shows statistics and trends

## Environment Variables

### Backend (.env)
- `REDDIT_CLIENT_ID` - Reddit API client ID
- `REDDIT_CLIENT_SECRET` - Reddit API secret
- `REDDIT_USER_AGENT` - Reddit user agent string
- `TWITTER_BEARER_TOKEN` - Twitter API bearer token
- `MONGODB_URI` - MongoDB connection string
- `OPENROUTER_API_KEY` - OpenRouter API key

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

## Dependencies

### Backend (Python)
- FastAPI - Web framework
- Motor - Async MongoDB driver
- PRAW - Reddit API
- Tweepy - Twitter API
- Transformers - Hugging Face models
- spaCy/NLTK - Text processing

### Frontend (Node.js)
- Next.js 14 - React framework
- globe.gl - 3D globe visualization
- Three.js - 3D graphics
- Framer Motion - Animations
- Plotly.js - Charts
- Tailwind CSS - Styling

## Deployment Considerations

- **Backend**: Can be deployed to Railway, Render, or any Python hosting
- **Frontend**: Can be deployed to Vercel, Netlify, or any static hosting
- **Database**: MongoDB Atlas (free tier available)
- **APIs**: Reddit (free), Twitter (may require paid tier), OpenRouter (pay-per-use)

