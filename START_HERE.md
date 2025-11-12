# 🚀 How to Start ScanLabel AI

## Quick Start (Easiest Method)

### Option 1: Use Batch Script (Windows)
1. **Double-click**: `START_SERVERS.bat`
2. **That's it!** Both servers will start automatically
3. Browser will open automatically

---

## Manual Start (Step by Step)

### Step 1: Start Backend (API Server)

**Open a terminal/PowerShell window:**

```powershell
cd "D:\ScanLabel AI"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Backend is running!** Keep this window open.

---

### Step 2: Start Frontend (Web Server)

**Open a NEW terminal/PowerShell window:**

```powershell
cd "D:\ScanLabel AI\frontend"
python -m http.server 8080
```

**You should see:**
```
Serving HTTP on 0.0.0.0 port 8080
```

**✅ Frontend is running!** Keep this window open too.

---

### Step 3: Open in Browser

**Open your browser and go to:**
```
http://localhost:8080
```

Or simply open: `frontend/index.html` directly in your browser (no server needed for basic testing)

---

## 📍 URLs

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ✅ Verify Everything Works

1. **Check Backend**: Open http://localhost:8000/health
   - Should show: `{"status":"healthy","model_loaded":true}`

2. **Check Frontend**: Open http://localhost:8080
   - Should see the ScanLabel AI interface

3. **Test Barcode Scan**: 
   - Go to "Barcode" tab
   - Enter: `5449000000996`
   - Click "Scan Product"

4. **Test Food Image**:
   - Go to "Food Image" tab
   - Upload an apple photo
   - Should recognize and show nutrition

---

## 🛑 How to Stop

**Press `Ctrl + C` in each terminal window** to stop the servers.

---

## 🔧 Troubleshooting

### Backend won't start?
- Check if port 8000 is already in use
- Make sure Python is installed
- Install dependencies: `pip install -r requirements.txt`

### Frontend won't start?
- Check if port 8080 is already in use
- Try a different port: `python -m http.server 8081`

### API not working?
- Make sure backend is running
- Check backend terminal for error messages
- Verify API key in `.env` file

---

## 🔑 API Keys Setup (Optional - for Food Image Recognition)

### Google Cloud Vision API (Recommended - Free Tier Available)

**Free Tier**: 1000 requests/month

**When Google asks "What data will you be accessing?"** → Select **"Application data"** (this is for server applications like our backend)

#### Setup Steps:

1. **Go to**: https://console.cloud.google.com/
2. **Create a project** (or select existing)
3. **Enable Vision API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"
4. **Create API Key** (Simplest Method):
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - **Optional**: Restrict the API key to "Cloud Vision API" only (more secure)
   - Copy the API key
5. **Add to `.env` file**:
   ```
   GOOGLE_VISION_API_KEY=your_api_key_here
   ```

**Note**: Google Vision API is now the PRIMARY method for food image recognition. Spoonacular is used as fallback.

**Alternative (More Secure)**: You can also use a Service Account JSON file instead of API key:

#### Service Account Setup (Optional - More Secure):

1. **Create Service Account**:
   - Service account name: `scanlabel-vision-api` (or any name you prefer)
   - Description: `Service account for ScanLabel AI food image recognition using Cloud Vision API`
   - Click "Create and Continue"

2. **Grant Permissions**:
   - Role: Select **"Cloud Vision API User"** (or search for it)
   - Click "Continue" → "Done"

3. **Create Key**:
   - Click on the service account you just created
   - Go to "Keys" tab → "Add Key" → "Create new key"
   - Select **JSON** format
   - Download the JSON file

4. **Set up in your project**:
   - Save the JSON file in your project root (e.g., `google-vision-key.json`)
   - Add to `.env`:
     ```
     GOOGLE_APPLICATION_CREDENTIALS=google-vision-key.json
     ```
   - **Note**: You'll need to update the code to use service account authentication instead of API key.

**Recommendation**: Use API key (simpler) unless you need the extra security of service accounts.

### Spoonacular API (Fallback - Optional)

If you want to use Spoonacular as backup:
1. **Sign up**: https://spoonacular.com/food-api
2. **Get API key** from dashboard
3. **Add to `.env` file**:
   ```
   SPOONACULAR_API_KEY=your_api_key_here
   ```

**Note**: Spoonacular free tier has Cloudflare protection and may be blocked. Google Vision is more reliable.

---

## 📝 Quick Commands

**Start Backend:**
```powershell
cd "D:\ScanLabel AI"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Start Frontend:**
```powershell
cd "D:\ScanLabel AI\frontend"
python -m http.server 8080
```

**View Logs:**
```powershell
Get-Content scanlabel_ai.log -Tail 50
```

---

## 🎯 That's It!

You're ready to use ScanLabel AI! 🎉
