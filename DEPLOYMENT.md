# 🚀 Deployment Guide

This guide covers deploying ScanLabel AI to various free hosting platforms.

## 📋 Best Free Hosting Options

### 1. **Railway** ⭐ (Recommended - Easiest)
**Free Tier:** $5/month credit (usually enough for small apps)

**Why Railway:**
- ✅ Easiest deployment (just connect GitHub)
- ✅ Auto-detects Python apps
- ✅ Free tier is generous
- ✅ Built-in PostgreSQL (if needed later)
- ✅ Automatic HTTPS

**Deploy Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Python and runs `uvicorn main:app`
6. Done! Your API is live

**Environment Variables (optional):**
- `PORT` - Auto-set by Railway
- `LOG_LEVEL` - Set to `INFO` or `DEBUG`

---

### 2. **Render** ⭐ (Best Free Tier)
**Free Tier:** 750 hours/month (enough for 24/7)

**Why Render:**
- ✅ True free tier (no credit card needed)
- ✅ Auto-deploy from GitHub
- ✅ Free SSL certificate
- ✅ Sleeps after 15 min inactivity (wakes on request)

**Deploy Steps:**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your repository
5. Settings:
   - **Build Command:** `pip install -r requirements.txt && python train_model.py`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3
6. Click "Create Web Service"
7. Wait ~5 minutes for first deploy

**Note:** First request after sleep takes ~30 seconds (cold start)

---

### 3. **Fly.io** 🐳 (Docker-based)
**Free Tier:** 3 shared VMs, 3GB storage

**Why Fly.io:**
- ✅ Docker-based (more control)
- ✅ Global edge deployment
- ✅ No sleep (always on)
- ✅ Great for production

**Deploy Steps:**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Sign up: `fly auth signup`
3. Deploy: `fly deploy`
4. Done!

**Commands:**
```bash
fly launch  # First time setup
fly deploy  # Deploy updates
fly status  # Check status
```

---

### 4. **Google Cloud Run** ☁️ (Most Generous)
**Free Tier:** 2 million requests/month, 360,000 GB-seconds

**Why Cloud Run:**
- ✅ Most generous free tier
- ✅ Pay only for what you use
- ✅ Auto-scales to zero
- ✅ Global CDN

**Deploy Steps:**
1. Install Google Cloud SDK
2. Create project: `gcloud projects create scanlabel-ai`
3. Build & deploy:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/scanlabel-ai
   gcloud run deploy --image gcr.io/PROJECT_ID/scanlabel-ai --platform managed
   ```
4. Done!

---

### 5. **Vercel** (Not Recommended for FastAPI)
**Note:** Vercel is optimized for serverless functions, not long-running FastAPI apps. It can work but requires adaptation.

**If you must use Vercel:**
- Use `vercel.json` config (already included)
- Deploy as serverless function
- May have cold start issues

---

## 🔧 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] `model.pkl` is committed (or train on first deploy)
- [ ] `requirements.txt` is up to date
- [ ] Environment variables are set (if needed)
- [ ] `PORT` environment variable is used (for platforms that set it)
- [ ] Health check endpoint works (`/health`)

## 📝 Environment Variables

Create a `.env` file (or set in hosting platform):

```env
PORT=8000
LOG_LEVEL=INFO
MODEL_PATH=model.pkl
OFF_API_BASE_URL=https://world.openfoodfacts.org/api/v0
OFF_API_TIMEOUT=10
```

## 🐳 Docker Deployment

If using Docker (Fly.io, Railway, etc.):

```bash
# Build image
docker build -t scanlabel-ai .

# Run locally
docker run -p 8000:8000 scanlabel-ai

# Or use docker-compose
docker-compose up
```

## 🔍 Post-Deployment

After deploying:

1. **Test the API:**
   ```bash
   curl https://your-app.railway.app/health
   curl "https://your-app.railway.app/scan?barcode=5449000000996"
   ```

2. **Check Logs:**
   - Railway: Dashboard → Logs
   - Render: Dashboard → Logs
   - Fly.io: `fly logs`

3. **Monitor Health:**
   - Use `/health` endpoint
   - Set up uptime monitoring (UptimeRobot, etc.)

## 🎯 Recommended Setup

**For Beginners:** Railway (easiest)
**For Best Free Tier:** Render (no credit card)
**For Production:** Fly.io or Google Cloud Run

## 📚 Additional Resources

- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)

## 🆘 Troubleshooting

### Model not loading?
- Ensure `model.pkl` is in repository
- Or add model training to build step

### Port errors?
- Use `$PORT` environment variable
- Most platforms set this automatically

### Build failures?
- Check Python version (3.11 recommended)
- Ensure all dependencies in `requirements.txt`
- Check build logs for errors

### Slow cold starts?
- Normal for Render (free tier sleeps)
- Consider Railway or Fly.io for always-on

---

**Need help?** Check the logs in your hosting platform dashboard!








