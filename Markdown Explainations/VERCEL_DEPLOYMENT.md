# Earth's Pulse Frontend - Vercel Deployment Guide

This guide will help you deploy the Earth's Pulse frontend to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. The Vercel CLI installed (optional): `npm i -g vercel`
3. Your backend API deployed and accessible via HTTPS

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Import your project to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Select the `frontend` directory as the root directory

3. **Configure the project**
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

4. **Add Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add the following variable:
     - **Name**: `NEXT_PUBLIC_BACKEND_URL`
     - **Value**: Your backend API URL (e.g., `https://your-backend-api.com`)
     - **Environment**: Production, Preview, Development (select all)

5. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete

### Option 2: Deploy via Vercel CLI

1. **Login to Vercel**
   ```bash
   vercel login
   ```

2. **Navigate to the frontend directory**
   ```bash
   cd frontend
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Follow the prompts**
   - Set up and deploy: `Y`
   - Which scope: Select your account
   - Link to existing project: `N`
   - Project name: `earth-pulse-frontend` (or your choice)
   - Directory: `./`
   - Override settings: `N`

5. **Set environment variables**
   ```bash
   vercel env add NEXT_PUBLIC_BACKEND_URL
   ```
   Enter your backend API URL when prompted

6. **Deploy to production**
   ```bash
   vercel --prod
   ```

## Environment Variables

The following environment variable is required:

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | `https://api.earthspulse.com` |

### Setting Environment Variables in Vercel

1. Go to your project dashboard
2. Click on "Settings"
3. Click on "Environment Variables"
4. Add `NEXT_PUBLIC_BACKEND_URL` with your backend URL
5. Redeploy your project

## Post-Deployment

### Verify Deployment

1. Visit your Vercel deployment URL
2. Check the browser console for any errors
3. Verify the globe loads correctly
4. Test the API connections

### Common Issues

#### Issue: Globe not loading
- **Solution**: Check that `three`, `three-globe`, and `globe.gl` patches are applied correctly
- The build process should automatically run `patch-package` via the postinstall script

#### Issue: API calls failing
- **Solution**: Verify `NEXT_PUBLIC_BACKEND_URL` is set correctly in Vercel environment variables
- Ensure your backend has CORS configured to allow requests from your Vercel domain

#### Issue: Build fails with "Module not found: three/webgpu"
- **Solution**: Ensure the `patches` directory is committed to git
- Verify `patch-package` runs during build (check build logs)

### CORS Configuration

Your backend needs to allow requests from your Vercel domain. Update your backend CORS settings:

```python
# In your FastAPI backend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-vercel-domain.vercel.app",
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Click on "Domains"
3. Add your custom domain
4. Follow the DNS configuration instructions
5. Update your backend CORS settings to include the new domain

## Automatic Deployments

Vercel automatically deploys:
- **Production**: Every push to the `main` branch
- **Preview**: Every push to other branches and pull requests

## Monitoring

- View deployment logs in the Vercel dashboard
- Check analytics and performance metrics
- Set up integration with monitoring tools if needed

## Local Development

To run locally with environment variables:

```bash
# Copy the example env file
cp .env.example .env.local

# Edit .env.local with your backend URL
# Then run the dev server
npm run dev
```

## Support

For issues related to:
- **Vercel**: Check [Vercel Documentation](https://vercel.com/docs)
- **Next.js**: Check [Next.js Documentation](https://nextjs.org/docs)
- **This project**: Open an issue in the repository
