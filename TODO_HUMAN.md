# Manual Setup Steps (Cannot Be Automated)

This document lists steps that require human interaction or manual configuration.

## 1. Web Scraping Setup (For Profile Data Fetching)

**Important**: System fetches PUBLIC data from Gmail/Instagram profiles for ANY user. No OAuth required. Users provide their own email/username during onboarding.

### Installation Requirements

1. **Install Python scraping libraries**:
   ```bash
   pip install beautifulsoup4 selenium instaloader email-validator
   ```

2. **For Selenium (dynamic content scraping)**:
   ```bash
   # Install ChromeDriver for Selenium
   brew install chromedriver  # macOS
   # or download from: https://chromedriver.chromium.org/
   ```

3. **Optional: Scraping API Service** (for better reliability):
   - Sign up for [ScraperAPI](https://www.scraperapi.com/) or similar service
   - Add to `.env`:
     ```
     SCRAPING_API_KEY=your_scraper_api_key
     ```
   - This helps avoid rate limiting and IP blocking

### How It Works

1. **User Onboarding Flow**:
   - User provides their Gmail email (e.g., "user@gmail.com")
   - User provides their Instagram username (e.g., "adventurer123")
   - System fetches PUBLICLY available data from these profiles

2. **Gmail Data Fetching**:
   - Attempts to fetch public profile data (name, profile picture if public)
   - Extracts name from email if profile not accessible
   - **Note**: DOB is typically not publicly available, so may not be fetched

3. **Instagram Data Fetching**:
   - Uses `instaloader` library to scrape public Instagram posts
   - Fetches last 20-30 public posts with captions and hashtags
   - Extracts bio information (if public)
   - Calculates adventurous_score based on hashtags (#skiing, #travel, etc.)

### Rate Limiting & Best Practices

1. **Implement rate limiting**:
   - Cache scraped data to avoid repeated requests for same user
   - Limit requests per IP address
   - Use delays between requests

2. **Handle edge cases**:
   - Private Instagram profiles: Gracefully handle, use only available data
   - Invalid usernames: Return error message
   - Network failures: Implement retry logic with exponential backoff

3. **Privacy compliance**:
   - Only fetch PUBLICLY available data
   - Respect robots.txt
   - Store user consent records
   - Allow users to delete their scraped data

### No Manual Setup Required

Unlike OAuth, this approach requires **NO manual application setup**. The system works for any user who provides their email and Instagram username. Just ensure:
- Python scraping libraries are installed
- ChromeDriver is available (if using Selenium)
- Optional: Scraping API key for production use

## 2. Stripe Test Account Setup

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
2. Copy Test Publishable Key and Test Secret Key
3. Add to `.env`:
   ```
   STRIPE_TEST_SECRET=sk_test_...
   STRIPE_TEST_PUBLISHABLE=pk_test_...
   ```
4. For webhook testing (local):
   ```bash
   # Install Stripe CLI
   brew install stripe/stripe-cli/stripe  # macOS
   
   # Login
   stripe login
   
   # Forward webhooks to local server
   stripe listen --forward-to http://localhost:8001/webhooks/stripe
   
   # Copy webhook signing secret
   STRIPE_WEBHOOK_SECRET_TEST=whsec_...
   ```

## 3. MongoDB Setup

### Option A: Local MongoDB
```bash
# Install MongoDB
brew install mongodb-community  # macOS
# or follow: https://www.mongodb.com/docs/manual/installation/

# Start MongoDB
brew services start mongodb-community  # macOS
# or: mongod --dbpath /data/db

# Add to .env
MONGO_URI=mongodb://localhost:27017/wandersure
```

### Option B: MongoDB Atlas (Cloud)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster
3. Create database user
4. Whitelist IP addresses (or 0.0.0.0/0 for development)
5. Get connection string:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/wandersure?retryWrites=true&w=majority
   ```

## 4. Voice API Setup (Optional)

### Option A: OpenAI Voice API
1. Get OpenAI API key with voice access
2. Add to `.env`:
   ```
   TTS_API_KEY=sk-...  # Uses OpenAI for TTS
   STT_API_KEY=sk-...  # Uses OpenAI Whisper for STT
   ```

### Option B: Google Cloud TTS/STT
1. Create Google Cloud project
2. Enable Cloud Text-to-Speech and Speech-to-Text APIs
3. Create service account and download JSON key
4. Set environment variable:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=./path/to/service-account-key.json
   TTS_API_KEY=google  # Use Google TTS
   STT_API_KEY=google   # Use Google STT
   ```

### Option C: Browser Built-in (No Setup)
- If no API keys provided, system uses browser's built-in Web Speech API (limited but works)

## 5. Email Service Setup (Optional, for Consent Receipts)

### Option A: SendGrid
1. Create SendGrid account
2. Create API key
3. Add to `.env`:
   ```
   SENDGRID_API_KEY=SG....
   EMAIL_SENDER=noreply@yourdomain.com
   ```

### Option B: AWS SES
1. Set up AWS SES in your region
2. Verify sender email
3. Add to `.env`:
   ```
   AWS_SES_REGION=ap-southeast-1
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   EMAIL_SENDER=noreply@yourdomain.com
   ```

## 6. GitHub Token Setup (For PR Creation)

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Add to `.env`:
   ```
   GITHUB_TOKEN=ghp_...
   GIT_REPO_URL=https://github.com/yourusername/msig-insurance-chatbot
   ```

## 7. Production Deployment Considerations

1. Set production domain in `.env` (for Stripe webhooks, email links):
   ```
   DOMAIN=https://wandersure.yourdomain.com
   ```
2. Ensure HTTPS is enabled (required for secure data handling)
3. Configure rate limiting for web scraping (avoid overwhelming services)
4. Set up monitoring for scraping success rates
5. Implement proper error handling for failed scraping attempts

## 8. Claims PDF Processing (One-time)

If you have `Claims_Data_DB.pdf`:
```bash
# Run one-time import script
python scripts/load_claims_from_pdf.py

# This populates MongoDB claims_cache collection
# If PDF not available, system uses existing PostgreSQL connection
```

## 9. Testing Checklist

Before creating PR, manually test:

- [ ] Gmail OAuth flow works and fetches profile
- [ ] Instagram OAuth works (or fallback manual input)
- [ ] Language switcher changes UI and responses
- [ ] Voice TTS works in all languages
- [ ] Voice STT transcribes correctly
- [ ] Stripe sandbox payment auto-completes
- [ ] New chat saves to history
- [ ] Itinerary analysis shows claims data
- [ ] Policy comparison shows quantitative scores
- [ ] Simplified policy wording displays correctly

## 10. Production Deployment Checklist

Before deploying to production:

- [ ] Change `DOMAIN` to production URL
- [ ] Update OAuth redirect URIs in Google/Instagram
- [ ] Use production MongoDB (Atlas recommended)
- [ ] Use production Stripe keys (not test keys)
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set up proper logging and monitoring
- [ ] Configure backup strategy for MongoDB
- [ ] Review and update CORS settings
- [ ] Set up rate limiting
- [ ] Enable MongoDB encryption at rest
- [ ] Configure PII redaction in logs

## Troubleshooting

### Profile Scraping Not Working
- Verify instaloader is installed: `pip install instaloader`
- Check Instagram username is valid and profile is public
- If rate limited, wait or use Scraping API service
- For private profiles, system will handle gracefully (use available data only)
- Check ChromeDriver is installed if using Selenium: `chromedriver --version`

### MongoDB Connection Fails
- Check MongoDB is running (local) or cluster is accessible (Atlas)
- Verify connection string format
- Check firewall/IP whitelist settings

### Stripe Webhook Not Received
- Verify webhook secret is correct
- Check Stripe CLI is forwarding correctly (local)
- Ensure endpoint is accessible from internet (production)

### Voice Not Working
- Check browser supports Web Speech API
- Verify API keys if using external services
- Check browser permissions for microphone

