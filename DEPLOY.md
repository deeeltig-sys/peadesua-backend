# Pɛ Adesua Backend — Deploy to Render

This folder is ready to deploy as-is. It's a Flask app that proxies the
frontend to Groq (model: llama-3.3-70b-versatile).

## What's in here
- `app.py` — the Flask app (Makaveli X system prompt baked in)
- `requirements.txt` — flask, flask-cors, requests, groq, gunicorn
- `render.yaml` — Render Blueprint (optional, for one-click setup)

## Step-by-step deploy

### 1. Push to GitHub
Create a new repo (e.g. `peadesua-backend`) and push this folder's contents
to it — `app.py`, `requirements.txt`, `render.yaml` all at the repo root.

```bash
cd peadesua-backend
git init
git add .
git commit -m "Pe Adesua backend v1"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/peadesua-backend.git
git push -u origin main
```

### 2. Create the Web Service on Render

**Option A — Blueprint (uses render.yaml automatically):**
1. Go to https://dashboard.render.com/blueprints
2. Click "New Blueprint Instance"
3. Connect the `peadesua-backend` repo
4. Render reads `render.yaml` and pre-fills everything
5. You'll be prompted for `GROQ_API_KEY` — paste your key
6. Click "Apply"

**Option B — Manual web service:**
1. Go to https://dashboard.render.com/
2. New → Web Service → connect the `peadesua-backend` repo
3. Settings:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free
4. Add environment variable:
   - `GROQ_API_KEY` = your Groq API key (from https://console.groq.com/keys)
5. Click "Create Web Service"

### 3. Wait for the build
Render will install dependencies and start the server. First deploy takes
2-4 minutes. Watch the logs — you should see something like:
```
Booting worker with pid: ...
```

### 4. Get your URL
Once live, Render gives you a URL like:
```
https://peadesua-backend.onrender.com
```

Test it:
```bash
curl https://peadesua-backend.onrender.com/
```
Should return:
```json
{"status": "ok", "service": "Pe Adesua backend", "model": "llama-3.3-70b-versatile"}
```

Test the actual endpoint:
```bash
curl -X POST https://peadesua-backend.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"How do I prepare for an exam I'm behind on?\"}"
```

### 5. Plug into the frontend
In `learnmore-project/www/index.html`, set:
```javascript
const BACKEND_URL = "https://peadesua-backend.onrender.com/ask";
```

Then `npx cap sync android` and rebuild the APK.

## Free tier note
Render's free web services spin down after ~15 min of inactivity and take
~30-60 seconds to wake up on the next request. The first message after
idle time will feel slow — this is normal on the free plan, not a bug.

## Where to get a Groq API key
1. https://console.groq.com/keys
2. Sign in, click "Create API Key"
3. Copy it — you won't see it again, paste it into Render's env var
