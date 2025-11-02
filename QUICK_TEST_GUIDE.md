# Quick Test Guide - Full System Verification

## 🎯 Test the Complete Flow in 5 Minutes

### Prerequisites
```bash
# 1. Start the backend server
cd /Users/racshanyaa/Documents/GitHub/msig-insurance-chatbot
python run_server.py

# 2. Start the frontend (in another terminal)
cd frontend
npm run dev

# 3. Start payment services (in another terminal)
cd Payments
docker-compose up -d
```

### Test Checklist

#### ✅ Test 1: User Onboarding
1. Open browser: http://localhost:3000
2. **Expected**: Onboarding modal appears automatically
3. Enter: Age = 35
4. Select interests: Skiing/Snowboarding, Scuba Diving
5. Select medical: High Blood Pressure
6. Click "Complete Setup"
7. **Expected**: Modal closes, welcome message appears

#### ✅ Test 2: Upload Itinerary
1. Click upload button (paperclip icon)
2. Upload a sample PDF or image of a travel booking
   - Or use a screenshot with: destination, dates, pax
3. **Expected**: 
   - Document processing message
   - Trip details extracted
   - Claims analysis if available
   - Policy recommendations appear

#### ✅ Test 3: Review Policies
1. **Expected**: See 3 policy cards displayed:
   - Scootsurance QSR022206 (Product A)
   - TravelEasy Policy QTD032212 (Product B)
   - TravelEasy Pre-Ex Policy QTD032212-PX (Product C)
2. Each should show:
   - Price in SGD
   - Match score
   - Key benefits
   - "Buy Now" button

#### ✅ Test 4: Purchase Flow
1. Click "Buy Now" on any policy
2. Fill in traveler details (if prompted)
3. Enter payment info:
   - Card: 4242 4242 4242 4242
   - Expiry: 12/34
   - CVC: 123
   - ZIP: 12345
4. Click "Complete Purchase"
5. **Expected**: Stripe checkout opens
6. Complete payment
7. **Expected**: Success message with policy number

#### ✅ Test 5: Policy Questions
After purchase or even without:
1. Ask: "Does this policy cover skiing?"
2. **Expected**: Conversational answer with policy details
3. Ask: "Can I cancel anytime?"
4. **Expected**: Cancellation policy explanation
5. Ask: "What about pre-existing conditions?"
6. **Expected**: Clear explanation (especially if Product C recommended)

### 🐛 Troubleshooting

#### Onboarding not appearing?
- Clear localStorage: `localStorage.clear()` in browser console
- Refresh page

#### No policies showing?
- Check server logs for "Taxonomy loaded successfully"
- Check "✅ Matched X applicable policies"
- Verify Policy_Wordings folder has 3 PDF files

#### Payment not working?
- Check Stripe key in .env file
- Verify DynamoDB is running: http://localhost:8010
- Check docker-compose logs: `docker-compose logs -f`

#### Policy questions vague?
- Check GROQ_API_KEY is set
- Look for API rate limits
- Verify conversation_handler logs

---

## 📊 Expected Results

### Onboarding
✅ Age saved: 35  
✅ Interests: ["Skiing/Snowboarding", "Scuba Diving"]  
✅ Medical: ["High Blood Pressure"]  

### Itinerary
✅ Destination extracted  
✅ Dates extracted  
✅ Pax count extracted  
✅ Activities detected  

### Policy Matching
✅ 3 policies returned  
✅ Product C (Pre-Ex) scores highest for medical conditions  
✅ Scores adjust based on age/activities  

### Payment
✅ Stripe session created  
✅ Payment recorded in DynamoDB  
✅ Webhook updates status to "completed"  

### Questions
✅ Insurance questions answered using policy data  
✅ Citations included  
✅ Conversational, natural responses  

---

## 🎉 Success Metrics

Your system is **fully functional** if:
- ✅ All 3 policies appear for any itinerary
- ✅ Scores are calculated and displayed
- ✅ Stripe checkout opens successfully
- ✅ Payments are recorded in DynamoDB
- ✅ Policy questions get detailed answers
- ✅ No hard-coded data or dummies
- ✅ Graceful error handling

---

## 📸 Sample Scenarios

### Scenario 1: Adventure Traveler
```
Age: 28
Interests: Skiing, Scuba Diving, Hiking
Medical: None
Trip: Japan, skiing, 7 days

Expected:
- Product C should score high for adventure activities
- All policies should appear
- Prices reflect trip details
```

### Scenario 2: Senior with Medical
```
Age: 65
Interests: Beach/Relaxation, Cultural
Medical: Diabetes, Heart Condition
Trip: Thailand, 10 days

Expected:
- Product C (Pre-Ex) should score highest
- Pre-existing coverage highlighted
- Medical benefits emphasized
```

### Scenario 3: Budget Traveler
```
Age: 22
Interests: City Tours, Shopping
Medical: None
Trip: Singapore weekend trip

Expected:
- Scootsurance should show competitive price
- Basic coverage sufficient
- Affordable options highlighted
```

---

## 🚀 Next Steps

Once tests pass:
1. Populate taxonomy with real policy data (optional)
2. Add more policy comparisons
3. Implement claims filing
4. Add payment history dashboard
5. Expand multilingual support

---

**Ready to Test?** Start with Test 1 and work through all 5! 🎉

