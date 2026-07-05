# Deployment Guide

How to deploy the QuensultingAI Voice Agent backend to production.

---

## Option 1: Railway (Recommended for Quick Deploy)

### Prerequisites
- [Railway account](https://railway.app/)
- GitHub repository linked

### Steps

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Initial voice agent deployment"
   git push origin main
   ```

2. **Create Railway Project**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Select your repository

3. **Set Environment Variables**
   - Go to project **Settings** → **Variables**
   - Add all variables from `.env.example`
   - For `GOOGLE_SERVICE_ACCOUNT_FILE`, you'll need to use a different approach (see below)

4. **Handle Service Account JSON**
   
   Since Railway doesn't support file uploads, encode the JSON as a base64 env variable:
   ```bash
   # Encode locally
   base64 -i service_account.json | pbcopy  # macOS
   ```
   - Add as `GOOGLE_SERVICE_ACCOUNT_BASE64` env variable
   - Update `config.py` to decode it at runtime (or use the JSON string directly with `gspread.service_account_from_dict()`)

5. **Configure Start Command**
   
   In Railway, set the start command:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

6. **Deploy**
   - Railway auto-deploys on push
   - Get your public URL from the **Settings** → **Domains** tab

---

## Option 2: Render

### Steps

1. **Create `render.yaml`** (already compatible with our structure):
   ```yaml
   services:
     - type: web
       name: quensultingai-voice-agent
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: "3.11"
   ```

2. **Push to GitHub** and connect to Render
3. **Set environment variables** in the Render dashboard
4. **Deploy** — Render will auto-build and deploy

---

## Option 3: Google Cloud Run

### Steps

1. **Create a `Dockerfile`**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

2. **Build and deploy**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/voice-agent
   gcloud run deploy voice-agent \
     --image gcr.io/PROJECT_ID/voice-agent \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Set environment variables** via Cloud Run console or `--set-env-vars` flag

---

## Post-Deployment Checklist

- [ ] Backend is accessible at public URL
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/docs` is accessible (should be disabled in production)
- [ ] Environment variables are set correctly
- [ ] Google Sheets is accessible (test by hitting `/check-availability`)
- [ ] Retell webhook URL is updated to your public URL
- [ ] Retell Function Node URLs are updated
- [ ] SMTP email sending works
- [ ] Run a test call through Retell dashboard
- [ ] Run a test call via actual phone

---

## Security Notes

- Set `APP_ENV=production` to disable `/docs` and `/redoc`
- Ensure `RETELL_WEBHOOK_SECRET` is set for signature verification
- Never expose `service_account.json` or `.env` in public repos
- Use HTTPS for all endpoints (Railway/Render provide this by default)
- Consider rate limiting for production traffic
