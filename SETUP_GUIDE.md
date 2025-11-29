# WanderSure Setup Guide

Complete guide to running the WanderSure chatbot system end-to-end.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- Node.js 18+ and npm
- Groq API key (get from https://console.groq.com/)

### 1. Backend Setup

```bash
# Navigate to project root
cd /path/to/msig-insurance-chatbot

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env and add your GROQ_API_KEY
# GROQ_API_KEY=gsk_your_actual_key_here

# Start the backend server
PORT=8002 python3 run_server.py
```

The backend will start on `http://localhost:8002`

**Verify it's running:**
```bash
curl http://localhost:8002/health
# Should return: {"status":"ok","service":"wandersure"}
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local if needed (defaults to http://localhost:8002)
# NEXT_PUBLIC_API_URL=http://localhost:8002

# Start the frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Test the System

```bash
# From project root, run smoke test
python3 test_smoke.py
```

Or manually test:
1. Open `http://localhost:3000` in your browser
2. Type "hi" in the chat
3. You should get a greeting response

## 🔧 Configuration

### Backend Environment Variables (.env)

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here
PORT=8002

# Optional - for claims database
CLAIMS_DB_HOST=hackathon-db.ceqjfmi6jhdd.ap-southeast-1.rds.amazonaws.com
CLAIMS_DB_PORT=5432
CLAIMS_DB_NAME=hackathon_db
CLAIMS_DB_USER=hackathon_user
CLAIMS_DB_PASSWORD=Hackathon2025!

# Optional - rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Frontend Environment Variables (frontend/.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8002
```

## 🐛 Troubleshooting

### "ERR_CONNECTION_REFUSED" Error

**Problem:** Frontend cannot connect to backend

**Solutions:**
1. **Check if backend is running:**
   ```bash
   curl http://localhost:8002/health
   ```
   If this fails, the backend is not running.

2. **Start the backend:**
   ```bash
   PORT=8002 python3 run_server.py
   ```
   Wait for "Application startup complete" message.

3. **Check port conflicts:**
   ```bash
   lsof -i :8002
   ```
   If something else is using port 8002, either:
   - Stop that process, or
   - Change PORT in .env to a different port (e.g., 8003)
   - Update frontend .env.local to match

4. **Verify environment variables:**
   ```bash
   # Backend
   python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('GROQ_API_KEY:', 'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET')"
   
   # Frontend
   cd frontend && cat .env.local
   ```

### Backend Crashes on Startup

**Check:**
1. Is GROQ_API_KEY set? Backend will exit if not set.
2. Are all dependencies installed? Run `pip install -r requirements.txt`
3. Check logs for specific error messages

### Frontend Shows "Connection Issue" Message

**This means:**
- Backend is not running, OR
- Backend is on a different port than frontend expects, OR
- Network/firewall blocking connection

**Fix:**
1. Ensure backend is running (see above)
2. Check that `NEXT_PUBLIC_API_URL` in frontend matches backend port
3. Restart frontend after changing .env.local

## 📊 Health Checks

### Backend Health Endpoint

```bash
curl http://localhost:8002/health
```

Returns:
```json
{
  "status": "ok",
  "service": "wandersure",
  "timestamp": "2024-01-01T00:00:00",
  "checks": {
    "api": "ok",
    "groq_client": "ok",
    "claims_db": "ok"
  }
}
```

### Frontend Health Check

The frontend automatically checks backend health on load. If backend is unavailable, you'll see a clear error message.

## 🧪 Running Tests

### Smoke Test

```bash
python3 test_smoke.py
```

This tests:
- ✅ Health endpoint
- ✅ Greeting endpoint  
- ✅ Ask endpoint (sends "hi" and verifies response)

### Manual Testing

1. **Test greeting:**
   ```bash
   curl "http://localhost:8002/api/greeting?user_id=test&language=en"
   ```

2. **Test ask:**
   ```bash
   curl -X POST http://localhost:8002/api/ask \
     -H "Content-Type: application/json" \
     -d '{"question":"hi","user_id":"test","language":"en"}'
   ```

## 🏗️ Architecture

```
┌─────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │   Backend   │
│  (Next.js)  │         │  (FastAPI)  │
│  Port 3000  │ <────── │  Port 8002  │
└─────────────┘         └─────────────┘
                              │
                              ├──> Groq API (LLM)
                              ├──> PostgreSQL (Claims DB)
                              └──> MongoDB (Optional - Chat History)
```

## 📝 API Endpoints

### Health
- `GET /health` - Health check
- `GET /healthz` - Alternative health check

### Chat
- `GET /api/greeting?user_id=...&language=en` - Get personalized greeting
- `POST /api/ask` - Send chat message

### Other
- `POST /api/extract` - Extract trip details from document
- `POST /api/quote` - Get insurance quotes
- `POST /api/purchase` - Complete purchase

See `http://localhost:8002/docs` for full API documentation.

## 🚢 Production Deployment

### Backend

1. Set environment variables in production environment
2. Use a process manager (PM2, systemd, etc.)
3. Configure reverse proxy (nginx) if needed
4. Set up monitoring and logging

### Frontend

1. Build for production:
   ```bash
   cd frontend
   npm run build
   ```

2. Set `NEXT_PUBLIC_API_URL` to production backend URL

3. Deploy to Vercel, Netlify, or your hosting provider

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Run `test_smoke.py` to diagnose connectivity
3. Check backend logs for error messages
4. Verify all environment variables are set correctly

## ✅ Verification Checklist

Before considering setup complete:

- [ ] Backend starts without errors
- [ ] `curl http://localhost:8002/health` returns OK
- [ ] Frontend starts without errors
- [ ] Frontend can connect to backend (no ERR_CONNECTION_REFUSED)
- [ ] Typing "hi" in chat returns a response
- [ ] Smoke test passes: `python3 test_smoke.py`

---

**Last Updated:** 2024-01-01
**Version:** 1.0.0

