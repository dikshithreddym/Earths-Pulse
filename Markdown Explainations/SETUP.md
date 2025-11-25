# 🚀 Quick Setup Guide

## Prerequisites

- **Node.js 18+** and npm/yarn
- **Python 3.9+** and pip
- **Docker** (optional, for containerized deployment)
- **MongoDB Atlas** account (free tier) or local MongoDB
- **Reddit API** credentials (free)
- **Twitter/X API** credentials (optional)
- **OpenRouter API** key (optional, for AI summaries)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
cd "Earth's Pulse"
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy env.example .env  # Windows
# or
cp env.example .env    # Mac/Linux

# Edit .env and add your API keys
# See env.example for required variables
```

### 3. Get API Credentials

#### Reddit API (Required)
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Choose "script" type
4. Copy `client_id` and `client_secret` to `.env`

#### MongoDB Atlas (Recommended)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Get connection string
4. Add to `.env` as `MONGODB_URI`

#### Twitter API (Optional)
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create app and get Bearer Token
3. Add to `.env` as `TWITTER_BEARER_TOKEN`

#### OpenRouter API (Optional)
1. Go to https://openrouter.ai/
2. Sign up and get API key
3. Add to `.env` as `OPENROUTER_API_KEY`

### 4. Run Backend

```bash
# Make sure you're in backend directory with venv activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### 5. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install

# Create .env file (optional, defaults to localhost:8000)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 6. Run Frontend

```bash
npm run dev
# or
yarn dev
```

Frontend will be available at: http://localhost:3000

### 7. Test the Application

1. Open http://localhost:3000 in your browser
2. The globe should load (may take a moment for first load)
3. If no data appears, trigger a refresh:
   - Go to http://localhost:8000/api/moods/refresh (POST request)
   - Or use the API directly to seed data

## Docker Setup (Alternative)

### Build and Run with Docker Compose

```bash
# From project root
docker-compose up --build
```

This will start both frontend and backend containers.

### Individual Docker Builds

**Backend:**
```bash
cd backend
docker build -t earth-pulse-backend .
docker run -p 8000:8000 --env-file .env earth-pulse-backend
```

**Frontend:**
```bash
cd frontend
docker build -t earth-pulse-frontend .
docker run -p 3000:3000 earth-pulse-frontend
```

## Troubleshooting

### Backend Issues

**Import Errors:**
- Make sure you're running from the `backend` directory
- Or set `PYTHONPATH` to include the backend directory

**Model Download Issues:**
- The Hugging Face model downloads automatically on first use
- This may take a few minutes and requires internet connection
- Model is cached after first download

**MongoDB Connection Issues:**
- App will use in-memory storage if MongoDB is unavailable
- Data will be lost on restart without MongoDB
- Check your `MONGODB_URI` format

### Frontend Issues

**Globe Not Loading:**
- Check browser console for errors
- Ensure backend is running on port 8000
- Check CORS settings in backend

**API Connection Errors:**
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running
- Check network tab in browser dev tools

### General Issues

**Port Already in Use:**
- Change ports in `docker-compose.yml` or command line
- Backend: `--port 8001`
- Frontend: Change in `package.json` scripts

**Rate Limiting:**
- Reddit and Twitter APIs have rate limits
- App includes mock data fallback when APIs are unavailable
- Consider adding delays between requests

## Next Steps

1. **Seed Initial Data**: Use `/api/moods/refresh` endpoint to fetch initial data
2. **Customize**: Modify colors, styles, and features in frontend components
3. **Add Features**: Implement additional visualizations or filters
4. **Deploy**: Use services like Vercel (frontend) and Railway/Render (backend)

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review API documentation at `/docs` endpoint
3. Check console logs for error messages

