# Deploying ScanLabel AI to Render.com

Complete step-by-step guide to deploy your ScanLabel AI backend to Render.com.

## Prerequisites

- GitHub account with access to https://github.com/isharaj177-star/scan_label_ai
- Render.com account (free tier works perfectly)
- Code pushed to GitHub repository

## Step 1: Prepare Your Repository

The repository is already configured with:
- ✅ `render.yaml` - Render configuration file
- ✅ `requirements.txt` - Production dependencies
- ✅ `Procfile` - Process file for deployment
- ✅ `runtime.txt` - Python version specification
- ✅ `.gitignore` - Prevents sensitive files from being committed

## Step 2: Push Code to GitHub

```bash
# Make sure you're in the project directory
cd "D:\ScanLabel AI"

# Configure git user (already done)
git config user.name "isharaj177-star"
git config user.email "<email>"  # Use actual email

# Add all files
git add .

# Create initial commit
git commit -m "Prepare ScanLabel AI for Render.com deployment"

# Push to GitHub
git push -u origin main
```

If you get an error about "main" vs "master" branch:
```bash
git branch -M main
git push -u origin main
```

## Step 3: Create New Web Service on Render

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com/
   - Click "New +" button
   - Select "Web Service"

2. **Connect GitHub Repository**
   - Click "Connect GitHub" if not already connected
   - Search for `scan_label_ai` repository
   - Click "Connect" next to it

3. **Configure Service** (Render will auto-detect from render.yaml):
   - **Name**: `scanlabel-ai` (or choose your own)
   - **Region**: Oregon (Free tier available)
   - **Branch**: `main`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && python train_model.py`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Instance Type**: Free

4. **Environment Variables** (IMPORTANT!):
   Click "Advanced" → "Add Environment Variable" and add:

   ```
   PYTHON_VERSION=3.11.0
   HOST=0.0.0.0
   LOG_LEVEL=INFO
   DEBUG=false
   RELOAD=false
   SPOONACULAR_API_KEY=<your-key-if-you-have-one>
   GOOGLE_VISION_API_KEY=<your-key-if-you-have-one>
   ```

   **Note**: API keys are optional. Barcode scanning works without them!

5. **Click "Create Web Service"**

## Step 4: Monitor Deployment

1. Render will start building your app
2. Watch the build logs in real-time
3. Build process:
   - Install Python 3.11
   - Install dependencies from requirements.txt
   - Train ML model (takes 1-2 minutes)
   - Start uvicorn server

4. Build typically takes 3-5 minutes

## Step 5: Deployment Complete!

Once deployed, you'll get a URL like:
```
https://scanlabel-ai.onrender.com
```

### Test Your Deployment

1. **Health Check**:
   ```
   https://scanlabel-ai.onrender.com/health
   ```
   Should return: `{"status":"healthy","model_loaded":true,"version":"1.0.0"}`

2. **API Docs**:
   ```
   https://scanlabel-ai.onrender.com/docs
   ```
   Interactive API documentation

3. **Scan Product** (example with Coca-Cola barcode):
   ```
   https://scanlabel-ai.onrender.com/scan?barcode=5449000000996
   ```

## Important Notes

### Free Tier Limitations

- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes 30-60 seconds (cold start)
- 750 hours/month free (sufficient for testing/demo)
- Limited to 512 MB RAM

### Keeping Service Active

To prevent spin-down, you can:
1. Upgrade to paid plan ($7/month)
2. Use a cron job/uptime monitoring service (UptimeRobot, etc.)
3. Accept the cold starts (for demo purposes)

### Model Training

The model is trained during deployment using `train_model.py`:
- Runs during build phase
- Takes about 60-90 seconds
- Uses sample food data
- Saved as `model.pkl`

### API Keys (Optional)

**Google Vision API**:
- Required for image food recognition
- Requires billing enabled (first 1000 requests/month are free)
- Barcode scanning works WITHOUT this!

**Spoonacular API**:
- Currently disabled in the code
- Not needed for core functionality

## Troubleshooting

### Build Fails

**Issue**: "Failed to build scikit-learn"
**Solution**: Render free tier should handle this. If it fails, check requirements.txt versions.

**Issue**: "Model training failed"
**Solution**: Check build logs. May need to ensure training data is present.

### Runtime Errors

**Issue**: "Port already in use"
**Solution**: Render automatically sets $PORT. Make sure start command uses `--port $PORT`

**Issue**: "Emoji encoding errors"
**Solution**: Already fixed! All emojis removed from print statements.

### API Not Responding

**Issue**: Cold start taking too long
**Solution**: Wait 60 seconds for first request after inactivity.

**Issue**: 404 errors
**Solution**: Ensure URL is correct. Root is `/`, scan endpoint is `/scan?barcode=...`

## Updating Your Deployment

To deploy updates:

```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically:
1. Detect the push
2. Start new build
3. Deploy updated version
4. Zero-downtime deployment!

## Cost Breakdown

**Free Tier** (Recommended for demo/testing):
- $0/month
- 750 hours/month
- Spins down after 15 min inactivity
- Perfect for this project!

**Starter Plan** ($7/month):
- Always on (no spin-down)
- Faster cold starts
- More resources

## Frontend Integration

Once backend is deployed, update your frontend to use:
```javascript
const API_URL = "https://scanlabel-ai.onrender.com";
```

## Support & Resources

- Render Documentation: https://render.com/docs
- Render Status: https://status.render.com/
- Community: https://community.render.com/

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Build completed successfully
- [ ] `/health` endpoint returns healthy status
- [ ] `/docs` shows API documentation
- [ ] `/scan?barcode=5449000000996` returns product data
- [ ] Frontend connected to deployed backend

---

**Your backend is now live and ready to scan products! 🎉**
