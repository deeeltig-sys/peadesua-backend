# Pɛ Adesua Backend (v1 - Online AI)

## What this is

A Flask backend that sits between your existing LearnMore/Pɛ Adesua Capacitor
app and Google's Gemini API. Every message the student sends gets wrapped
with a system prompt that gives Pɛ Adesua the Makaveli X reasoning style
(strategic, disciplined, clear-eyed, Pan-African) - distilled from your two
books, without exposing the books themselves.

## 1. Get a Gemini API key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with a Google account, click "Create API key"
3. Copy the key

This is far easier than Arkesel - no business verification, instant.

## 2. Run locally

```bash
cd peadesua-backend
python -m venv venv
venv\Scripts\activate          (Windows)
source venv/bin/activate       (Mac/Linux)

pip install -r requirements.txt

# Set your API key
set GEMINI_API_KEY=your_key_here        (Windows cmd)
$env:GEMINI_API_KEY="your_key_here"     (Windows PowerShell)
export GEMINI_API_KEY=your_key_here     (Mac/Linux)

python app.py
```

Server runs at http://127.0.0.1:5001

## 3. Test it

```bash
curl -X POST http://127.0.0.1:5001/ask -H "Content-Type: application/json" -d "{\"message\":\"How do I prepare for an exam I'm behind on?\"}"
```

You should get back a response in the Pɛ Adesua voice - strategic, direct,
focused on concrete next actions.

## 4. Connect your existing frontend

In your LearnMore web app (the one already wrapped by Capacitor into the
working APK), replace the local/offline AI call with a fetch to this
backend:

```javascript
async function askPeAdesua(message, history = []) {
  const response = await fetch('https://YOUR_DEPLOYED_BACKEND_URL/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history })
  });
  const data = await response.json();
  return data.reply || data.error;
}
```

`history` is optional - an array of `{role: "user"|"model", text: "..."}`
for multi-turn context.

## 5. Deploy to Render

1. Push this folder to a GitHub repo (or a subfolder of an existing one)
2. Create a new Web Service on Render, point it at the repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app` (add `gunicorn` to requirements.txt for production)
5. Add environment variable: `GEMINI_API_KEY` = your key
6. Deploy - you get a live URL like `https://peadesua-backend.onrender.com`

Update your frontend's fetch URL to this deployed URL, rebuild the APK with
Capacitor (same process as before), done.

## 6. Branding (Law 1 - Never Outshine the Master)

USTED comes first and larger. ProjectX comes second and smaller - you are
the builder *for* the institution, not competing with it visually.

```html
<header style="text-align:center; padding:1rem;">
  <img src="assets/usted-logo.png" alt="USTED" style="height:60px; background:white; border-radius:8px; padding:4px; margin-bottom:6px;">
  <br>
  <img src="assets/projectx-logo.png" alt="ProjectX" style="height:28px; vertical-align:middle; opacity:0.85;">
</header>
```

Place the logo files in your Capacitor app's `assets` or `public` folder
before building the APK.

## Security note (v1, accepted risk)

The Gemini key lives server-side in this Flask app's environment variables -
NOT in the APK. The app calls your Flask backend, your backend calls Gemini.
This already solves the original exposed-key problem from the offline build,
without needing extra auth for v1.

## What's NOT in this v1

- No book content sent to the AI (only distilled principles in the system prompt)
- No user accounts / chat history persistence (each request is stateless unless
  you pass `history` from the frontend's local state)
- No rate limiting (add later if usage grows - Gemini free tier has its own limits)
