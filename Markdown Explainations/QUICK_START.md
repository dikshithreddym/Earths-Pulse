# ⚡ Quick Start Guide

Get Earth's Pulse running in 5 minutes!

## 🎯 Fastest Setup (Mock Data Mode)

If you just want to see it work without API keys:

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### Seed Sample Data
```bash
# In backend directory with venv activated
python scripts/seed_data.py
```

Open http://localhost:3000 - You should see the globe with data points!

## 🔑 Full Setup (With Real APIs)

1. **Get Reddit API** (2 minutes):
   - Go to https://www.reddit.com/prefs/apps
   - Create app → Get client_id and secret

2. **Get MongoDB** (3 minutes):
   - Go to https://www.mongodb.com/cloud/atlas
   - Create free cluster → Get connection string

3. **Configure**:
   ```bash
   cd backend
   copy env.example .env  # Windows
   # Edit .env with your keys
   ```

4. **Run**:
   ```bash
   # Backend
   uvicorn main:app --reload
   
   # Frontend (new terminal)
   cd frontend
   npm run dev
   ```

5. **Trigger Data Fetch**:
   - Visit: http://localhost:8000/api/moods/refresh
   - Or use: `curl -X POST http://localhost:8000/api/moods/refresh`

## 🐳 Docker (Easiest)

```bash
# From project root
docker-compose up --build
```

Visit http://localhost:3000

## 📝 What You'll See

- **3D Globe**: Interactive Earth with colored sentiment points
- **Sidebar**: Statistics, trends, and AI summary
- **Auto-Refresh**: Updates every 30 seconds
- **Hover Tooltips**: See emotion details on points

## 🆘 Troubleshooting

**No data showing?**
- Run seed script: `python backend/scripts/seed_data.py`
- Or trigger refresh: POST to `/api/moods/refresh`

**Backend won't start?**
- Check Python version: `python --version` (need 3.9+)
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start?**
- Check Node version: `node --version` (need 18+)
- Install dependencies: `npm install`

**Globe not loading?**
- Check browser console for errors
- Ensure backend is running on port 8000
- Check CORS settings

## 🎨 Customize

- **Colors**: Edit `frontend/components/Globe.tsx` → `getColorForSentiment()`
- **Refresh Rate**: Edit `frontend/app/page.tsx` → `setInterval(..., 30000)`
- **Point Size**: Edit `frontend/components/Globe.tsx` → `size: 0.5`

## 📚 Next Steps

- Read `SETUP.md` for detailed instructions
- Read `PROJECT_STRUCTURE.md` for code organization
- Check API docs at http://localhost:8000/docs

Happy hacking! 🌍✨

