# WanderSure Setup Guide

## 🎯 Complete Setup Instructions

### Step 1: Prerequisites
- Python 3.10 or higher
- Node.js 18+ (for frontend)
- Docker & Docker Compose (for payment services)
- Groq API key ([Get one here](https://console.groq.com/))

### Step 2: Clone & Setup Backend

```bash
cd ancileo-msig

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add:
# GROQ_API_KEY=your_groq_api_key_here
# STRIPE_SECRET_KEY=sk_test_... (optional, for payments)
# STRIPE_WEBHOOK_SECRET=whsec_... (optional, for payments)
```

### Step 3: Setup Payment Services (Optional, for Block 4)

```bash
cd Payments

# Create .env file in Payments/
echo "STRIPE_WEBHOOK_SECRET=whsec_test_your_secret" > .env

# Start services
docker-compose up -d

# Verify services are running
curl http://localhost:8086/health
curl http://localhost:8085/health
```

### Step 4: Run the Backend Server

```bash
# Option 1: Use the start script
./start.sh

# Option 2: Run directly
python run_server.py

# Server runs on http://localhost:8001
```

### Step 5: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local

# Run development server
npm run dev

# Frontend runs on http://localhost:3000
```

### Step 6: Test the System

```bash
# Run test suite
python test_system.py
```

## 🎨 Using the System

### Via Web Interface
1. Open http://localhost:3000
2. Start chatting with WanderSure
3. Try sample questions:
   - "Compare medical coverage between TravelEasy and Scootsurance"
   - "I'm traveling to Japan next week for skiing - what do you recommend?"
   - "What does trip cancellation cover?"

### Via API

```bash
# Ask a question
curl -X POST http://localhost:8001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is travel insurance?"}'

# Generate a quote
curl -X POST http://localhost:8001/api/quote \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Japan",
    "start_date": "2024-12-20",
    "end_date": "2024-12-27",
    "travelers": 1,
    "ages": [30],
    "activities": ["skiing"]
  }'

# Get risk assessment
curl -X POST http://localhost:8001/api/risk \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Japan",
    "activities": ["skiing"],
    "duration": 7,
    "age": 30
  }'
```

## 🔧 Troubleshooting

### Issue: "GROQ_API_KEY not set"
**Solution**: Make sure you've created `.env` file with your Groq API key.

### Issue: PDF extraction fails
**Solution**: 
- Check that `Policy_Wordings/` directory exists
- Ensure PDFs are readable
- Try: `pip install --upgrade PyPDF2 pdfplumber`

### Issue: Payment services not working
**Solution**:
- Check Docker is running: `docker ps`
- Verify services: `curl http://localhost:8086/health`
- Check DynamoDB: Open http://localhost:8010

### Issue: Frontend can't connect to backend
**Solution**:
- Verify backend is running on port 8001
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Check CORS settings in `run_server.py`

## 📚 Features Overview

✅ **Block 1: Policy Intelligence**
- Extract and normalize insurance policies
- Compare policies side-by-side
- Explain coverage with citations
- Check eligibility

✅ **Block 2: Conversational Magic**
- Natural language Q&A
- Sentiment detection
- Multi-language support
- Conversation memory

✅ **Block 3: Document Intelligence**
- Extract trip info from PDFs/images
- Generate personalized quotes
- Activity-based pricing

✅ **Block 4: Seamless Commerce**
- Stripe payment integration
- DynamoDB status tracking
- Webhook handling

✅ **Block 5: Predictive Intelligence**
- Risk assessment
- Claims data analysis
- Personalized recommendations

## 🚀 Production Deployment

1. **Backend**: Deploy to AWS/Render/GCP
   - Set production environment variables
   - Use production DynamoDB (not local)
   - Configure proper CORS

2. **Frontend**: Deploy to Vercel/Netlify
   - Set `NEXT_PUBLIC_API_URL` to production backend
   - Build: `npm run build`

3. **Payments**: 
   - Use production Stripe keys
   - Configure webhook endpoint
   - Set up email service for policy delivery

## 💡 Next Steps

- Extract claims data from PDF automatically
- Add more language support
- Integrate with actual pricing APIs
- Add policy document generation
- Implement user authentication
- Add analytics and monitoring

