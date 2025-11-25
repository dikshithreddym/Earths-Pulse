# Vercel Deployment Checklist ✅

Use this checklist to ensure your Earth's Pulse frontend is ready for Vercel deployment.

## Pre-Deployment Checklist

### 1. Code Preparation
- [x] Remove `output: 'standalone'` from `next.config.js` (Vercel handles this)
- [x] Ensure `postinstall` script runs `patch-package` in `package.json`
- [x] Verify `patches/` directory contains required patches
- [x] Check that `lib/three-stubs/` directory exists with webgpu.js and tsl.js

### 2. Environment Variables
- [ ] Create `.env.example` file with all required variables
- [ ] Ensure `.env.local` is in `.gitignore`
- [ ] Document `NEXT_PUBLIC_BACKEND_URL` requirement

### 3. Git Repository
- [ ] Commit all changes to git
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```
- [ ] Ensure `.gitignore` excludes:
  - `node_modules/`
  - `.next/`
  - `.env*.local`
  - `.env`

### 4. Backend Configuration
- [ ] Backend is deployed and accessible via HTTPS
- [ ] Backend CORS allows Vercel domains
- [ ] Backend API URL is ready (e.g., `https://api.yourbackend.com`)

## Vercel Setup

### 1. Create Vercel Project
- [ ] Go to [vercel.com/new](https://vercel.com/new)
- [ ] Import your GitHub repository
- [ ] Select the repository containing your project

### 2. Configure Project Settings
- [ ] **Framework Preset**: Next.js (auto-detected)
- [ ] **Root Directory**: `frontend` ⚠️ IMPORTANT
- [ ] **Build Command**: `npm run build` (default)
- [ ] **Output Directory**: `.next` (default)
- [ ] **Install Command**: `npm install` (default)
- [ ] **Node.js Version**: 18.x or 20.x (recommended)

### 3. Environment Variables
Add in Vercel Dashboard (Settings → Environment Variables):

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_BACKEND_URL` | Your backend URL (e.g., `https://api.yourbackend.com`) | Production, Preview, Development |

⚠️ **Important**: 
- Make sure there's NO trailing slash in the URL
- Use HTTPS in production
- Apply to all environments (Production, Preview, Development)

### 4. Deploy
- [ ] Click "Deploy"
- [ ] Wait for build to complete (2-5 minutes)
- [ ] Check build logs for any errors

## Post-Deployment Verification

### 1. Check Build Logs
- [ ] Verify `patch-package` ran successfully
- [ ] No errors related to `three/webgpu` or `three/tsl`
- [ ] Build completed successfully

### 2. Test the Application
- [ ] Visit your Vercel deployment URL
- [ ] Open browser DevTools Console
- [ ] Check for any JavaScript errors
- [ ] Verify the globe loads correctly
- [ ] Test API connections:
  - [ ] Globe data loads
  - [ ] Summary generates
  - [ ] Audio playback works
  - [ ] City data displays

### 3. Test API Connectivity
Open DevTools Network tab and check:
- [ ] API requests go to correct backend URL
- [ ] No CORS errors in console
- [ ] API responses return successfully (200 status)
- [ ] Data displays correctly on the frontend

### 4. Performance Check
- [ ] Run Lighthouse audit (DevTools → Lighthouse)
- [ ] Check Core Web Vitals
- [ ] Verify page loads in reasonable time (<5s)

## Common Issues & Solutions

### Issue: Build fails with "Module not found: three/webgpu"
**Solution:**
1. Ensure `patches/` directory is committed to git
2. Verify `postinstall` script in package.json: `"postinstall": "patch-package"`
3. Check Vercel build logs to confirm patch-package ran
4. Redeploy if needed

### Issue: API calls return CORS errors
**Solution:**
1. Verify `NEXT_PUBLIC_BACKEND_URL` is set in Vercel
2. Check backend CORS configuration includes your Vercel domain
3. Ensure backend allows `https://*.vercel.app`

### Issue: Environment variable not working
**Solution:**
1. Verify variable name starts with `NEXT_PUBLIC_` for client-side access
2. Check variable is set in correct environment (Production/Preview/Development)
3. Redeploy after adding/changing environment variables

### Issue: Globe displays but no data loads
**Solution:**
1. Check browser console for API errors
2. Verify backend URL is correct and accessible
3. Test backend health endpoint directly: `https://your-backend.com/api/health`
4. Check backend CORS configuration

### Issue: Build succeeds but page shows errors
**Solution:**
1. Check browser console for specific errors
2. Verify all dependencies installed correctly
3. Check for missing environment variables
4. Test locally with production build: `npm run build && npm start`

## Updating Your Deployment

### For Code Changes
```bash
git add .
git commit -m "Your changes"
git push origin main
```
Vercel will automatically deploy when you push to main.

### For Environment Variable Changes
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Update the variable
3. Redeploy: Deployments → Latest → Redeploy

### For Preview Deployments
- Every pull request gets its own preview URL
- Test changes before merging to main
- Preview deployments use Preview environment variables

## Custom Domain Setup (Optional)

### 1. Add Domain in Vercel
- [ ] Go to Project Settings → Domains
- [ ] Add your custom domain
- [ ] Follow DNS configuration instructions

### 2. Update Backend CORS
- [ ] Add your custom domain to backend CORS origins
- [ ] Redeploy backend if needed

### 3. Update Environment Variables
- [ ] Update any URLs that reference the domain
- [ ] Test with custom domain

## Monitoring & Maintenance

### Regular Checks
- [ ] Monitor deployment frequency and success rate
- [ ] Check Vercel Analytics for performance metrics
- [ ] Review error logs in Vercel Dashboard
- [ ] Keep dependencies updated

### Performance Monitoring
- [ ] Set up Vercel Analytics (optional)
- [ ] Monitor Core Web Vitals
- [ ] Check bundle size in build logs
- [ ] Review API response times

### Security
- [ ] Keep dependencies updated
- [ ] Review Vercel security best practices
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS only

## Success Criteria

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ Application loads at Vercel URL
- ✅ Globe renders correctly
- ✅ API connections work
- ✅ No console errors
- ✅ Data displays correctly
- ✅ Audio playback works
- ✅ Lighthouse score > 80

## Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **Project Issues**: Open an issue in your repository
- **Vercel Support**: https://vercel.com/support

---

**Last Updated**: November 9, 2025
**Version**: 1.0.0
