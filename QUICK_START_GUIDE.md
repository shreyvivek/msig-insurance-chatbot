# Quick Start Guide - Advanced Personalization Features

## Prerequisites Checklist

Before starting implementation, ensure you have:

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed  
- [ ] MongoDB installed (local or Atlas account)
- [ ] Stripe test account
- [ ] Groq API key (or OpenAI API key)
- [ ] Optional: Scraping API account (for production reliability)

## Step 1: Environment Setup

```bash
# 1. Clone/navigate to repository
cd msig-insurance-chatbot

# 2. Copy environment template
cp env.example .env

# 3. Edit .env with required values (see TODO_HUMAN.md for scraping setup)
nano .env  # or use your preferred editor
```

### Minimum Required Variables:
```bash
GROQ_API_KEY=gsk_...           # Required
MONGO_URI=mongodb://...        # Required
STRIPE_TEST_SECRET=sk_test_... # Required for payments
DOMAIN=http://localhost:3000   # Required for Stripe webhooks
```

### Optional (with fallbacks):
```bash
SCRAPING_API_KEY=...           # Optional - for production scraping reliability
TTS_API_KEY=...                # Optional - uses browser TTS if not provided
STT_API_KEY=...                # Optional - uses browser STT if not provided
```

## Step 2: Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Install new dependencies
pip install pymongo pymongo-encryption beautifulsoup4 selenium instaloader email-validator camelot-py tabula-py

# Frontend dependencies (if not already installed)
cd frontend
npm install
```

## Step 3: Database Setup

### Local MongoDB:
```bash
# Start MongoDB
brew services start mongodb-community  # macOS
# or: sudo systemctl start mongod      # Linux

# Verify it's running
mongosh  # Should connect successfully
```

### MongoDB Atlas (Cloud):
1. Create free cluster at https://www.mongodb.com/cloud/atlas
2. Get connection string
3. Add to `.env`: `MONGO_URI=mongodb+srv://...`

## Step 4: Web Scraping Setup (See TODO_HUMAN.md for Details)

### Installation:
1. **Install scraping libraries**: Already in requirements.txt
2. **Install ChromeDriver** (for Selenium, if needed):
   ```bash
   brew install chromedriver  # macOS
   ```
3. **Optional: Scraping API**: Sign up at ScraperAPI.com for production use

### How It Works:
- **NO OAuth setup required** - works for any user
- Users provide their Gmail email and Instagram username during onboarding
- System fetches PUBLIC data from these profiles automatically
- See TODO_HUMAN.md Section 1 for details

## Step 5: Implementation Order

Follow the implementation phases in `IMPLEMENTATION_PLAN.md`:

1. **Phase 1**: Database setup (MongoDB models)
2. **Phase 2**: Claims loader and risk scorer
3. **Phase 3**: Policy comparator
4. **Phase 4**: API endpoints (start with one router)
5. **Phase 5**: Services (implement one at a time)
6. **Phase 6**: Frontend components (test each incrementally)
7. **Phase 7**: Background workers
8. **Phase 8**: Testing
9. **Phase 9**: Documentation

## Step 6: Test Each Feature

### Test Risk Scorer:
```bash
python -c "
from services.risk_scorer import RiskScorer
scorer = RiskScorer()
risk = scorer.predict({
    'destination': 'Japan',
    'activities': ['skiing'],
    'age': 32,
    'adventurous_score': 0.8
})
print(risk)
"
```

### Test Policy Comparator:
```bash
curl -X POST http://localhost:8001/v1/policy/compare-quant \
  -H "Content-Type: application/json" \
  -d '{
    "policy_ids": ["TravelEasy", "Scootsurance"],
    "scenario": {
      "destination": "Japan",
      "activities": ["skiing"],
      "age": 32
    }
  }'
```

### Test Language Switch:
1. Start server: `python run_server.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000
4. Click language switcher → Select Tamil
5. Ask question → Verify Tamil response

## Step 7: Run Tests

```bash
# Backend tests
pytest tests/

# Frontend tests
cd frontend
npm run test

# Integration tests
pytest tests/integration/
```

## Step 8: Create PR

```bash
# Create feature branch
git checkout -b feature/wandersure-advanced-personalization

# Commit changes
git add .
git commit -m "feat: Implement advanced personalization features"

# Push and create PR
git push origin feature/wandersure-advanced-personalization
gh pr create --title "Advanced Personalization Features" --body "Implements all 8 features..."
```

## Common Issues & Solutions

### Issue: MongoDB Connection Error
**Solution**: Verify MongoDB is running and MONGO_URI is correct
```bash
mongosh  # Test connection
```

### Issue: Profile Scraping Not Working
**Solution**: 
- Verify instaloader is installed: `pip install instaloader`
- Check Instagram username is valid and profile is public
- If rate limited, wait or use Scraping API service
- Private profiles handled gracefully (system uses available data only)

### Issue: Voice Not Working
**Solution**: 
- Check browser permissions for microphone
- If using external API, verify API keys
- Fallback: System uses browser Web Speech API

### Issue: Claims PDF Cannot Be Parsed
**Solution**: System falls back to existing PostgreSQL connection. PDF parsing is enhancement only.

## Next Steps After Implementation

1. Review `DEPLOYMENT.md` for production setup
2. Follow `DEMO_RUNBOOK.md` for demo preparation
3. Test all acceptance criteria from IMPLEMENTATION_PLAN.md
4. Update README.md with new features
5. Create PR following checklist in IMPLEMENTATION_PLAN.md

## Need Help?

- See `IMPLEMENTATION_PLAN.md` for detailed implementation steps
- See `TODO_HUMAN.md` for manual setup instructions
- See `DEPLOYMENT.md` for production deployment
- Check existing code in repository for patterns

