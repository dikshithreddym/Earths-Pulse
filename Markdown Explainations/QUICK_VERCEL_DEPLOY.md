# 🚀 Quick Vercel Deployment Guide

Get your Earth's Pulse frontend live on Vercel in 5 minutes!

## Prerequisites
- ✅ Backend API deployed and accessible via HTTPS
- ✅ Vercel account (free at [vercel.com](https://vercel.com))
- ✅ Code pushed to GitHub

## Step-by-Step Deployment

### 1️⃣ Push Your Code to GitHub

```bash
# From the project root directory
cd "C:\Users\diksh\Desktop\Hack Trent\Earth-s-Pulse"

# Stage all changes
git add .

# Commit changes
git commit -m "Prepare frontend for Vercel deployment"

# Push to GitHub
git push origin main
```

### 2️⃣ Import to Vercel

1. Go to **[vercel.com/new](https://vercel.com/new)**
2. Click **"Import Project"**
3. Select your GitHub repository: **Earth-s-Pulse**
4. Click **"Import"**

### 3️⃣ Configure Project Settings

**CRITICAL**: Set the root directory!

```
Root Directory: frontend
```

Click **"Edit"** next to Root Directory and type: `frontend`

Other settings (keep defaults):
- ✅ Framework Preset: **Next.js**
- ✅ Build Command: `npm run build`
- ✅ Output Directory: `.next`
- ✅ Install Command: `npm install`

### 4️⃣ Add Environment Variable

Click **"Environment Variables"** and add:

```
Name:  NEXT_PUBLIC_BACKEND_URL
Value: https://your-backend-api.com
```

**⚠️ Replace `https://your-backend-api.com` with your actual backend URL!**

Select all environments:
- ✅ Production
- ✅ Preview  
- ✅ Development

### 5️⃣ Deploy!

Click **"Deploy"** and wait 2-5 minutes.

## ✅ Verify Deployment

Once deployed, visit your URL and check:

1. **Globe loads** ✓
2. **No console errors** ✓
3. **Data appears** ✓
4. **Summary generates** ✓

### Check in Browser DevTools (F12):

**Console tab** - Should be clean (no red errors)
**Network tab** - API calls should return 200 status

## 🔧 If Something Goes Wrong

### Issue: Globe doesn't load / "Module not found: three/webgpu"

Check Vercel build logs:
1. Go to Vercel Dashboard → Deployments
2. Click on latest deployment
3. Check "Building" logs
4. Look for `patch-package` - should show "Applying patches..."

If patches didn't apply, check:
- `patches/` folder is in git
- `package.json` has `"postinstall": "patch-package"`

### Issue: API calls fail / CORS errors

1. Check environment variable is set correctly in Vercel
2. Verify backend CORS includes your Vercel domain
3. Test backend directly: `https://your-backend.com/api/health`

### Issue: Environment variable not working

1. Verify it starts with `NEXT_PUBLIC_`
2. Check it's set in the correct environment
3. **Redeploy** after adding environment variables

## 🎯 Your URLs

After deployment, you'll get:

- **Production**: `https://earth-s-pulse.vercel.app`
- **Every branch**: Gets its own preview URL
- **Every PR**: Gets a unique preview URL

## 📱 Next Steps

### Add Custom Domain (Optional)
1. Vercel Dashboard → Settings → Domains
2. Add your domain
3. Update DNS settings
4. Add domain to backend CORS

### Enable Analytics
1. Vercel Dashboard → Analytics
2. Enable Web Analytics
3. Monitor performance

### Set Up Monitoring
1. Check deployment status regularly
2. Review Core Web Vitals
3. Monitor API response times

## 📚 Full Documentation

For detailed information, see:
- [`VERCEL_DEPLOYMENT.md`](./VERCEL_DEPLOYMENT.md) - Complete guide
- [`DEPLOYMENT_CHECKLIST.md`](./DEPLOYMENT_CHECKLIST.md) - Detailed checklist

## 🆘 Need Help?

**Common Resources:**
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js on Vercel](https://vercel.com/docs/frameworks/nextjs)
- [Vercel Support](https://vercel.com/support)

**Project-Specific:**
- Check `TROUBLESHOOTING.md` for known issues
- Open an issue on GitHub
- Review build logs in Vercel Dashboard

---

**✨ That's it! Your Earth's Pulse frontend should now be live on Vercel!**
