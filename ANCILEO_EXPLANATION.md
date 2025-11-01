# What is Ancileo Doing in This System?

## Overview

**Ancileo** is an external travel insurance API service that provides:
1. **Additional Insurance Policies** - Fetches real-time insurance quotes from Ancileo's marketplace
2. **Automated Purchase Processing** - Handles the complete purchase flow for insurance policies
3. **Dynamic Pricing** - Gets live pricing based on trip details (destination, dates, travelers)

## How It Works

### 1. **Fetching Additional Policies** (Primary Function)

When a user requests insurance quotes:

1. **Local Policies First**: The system first uses pre-loaded policies (TravelEasy, Scootsurance) from PDF files
2. **Ancileo API Call**: If Ancileo API key is configured, the system ALSO fetches additional policies from Ancileo
3. **Combined Results**: Both local and Ancileo policies are merged and presented to the user

**Code Location**: 
- `policy_intelligence.py` - `get_policy_list()` method (line ~159)
- `run_server.py` - `/api/quote` endpoint (line ~289)

### 2. **Real-Time Quote Generation**

When quotes are requested:
- **Trip Details**: User provides destination, dates, number of travelers
- **Ancileo Pricing API**: Called with trip parameters to get real-time quotes
- **Policy Options**: Returns available insurance plans with pricing from Ancileo's marketplace

**Code Location**: 
- `ancileo_api.py` - `get_quote()` method (line ~34)
- `run_server.py` - `/api/quote` endpoint uses Ancileo as primary source when available

### 3. **Automated Purchase Processing**

When a user wants to buy insurance:
- **Quote Selection**: User selects a policy from Ancileo quotes
- **Purchase API**: Calls Ancileo's purchase endpoint with:
  - Quote ID
  - Offer ID
  - Product code
  - Traveler information
- **Policy Issuance**: Ancileo processes the purchase and returns policy number/confirmation

**Code Location**:
- `ancileo_api.py` - `purchase_policy()` method (line ~195)
- `run_server.py` - `/api/ancileo/purchase` endpoint (line ~488)

## Benefits

1. **More Policy Options**: Users get access to Ancileo's full marketplace of insurance products
2. **Real-Time Pricing**: Live quotes based on current rates and trip specifics
3. **Seamless Purchase**: Complete insurance purchase without leaving the chatbot
4. **Reliable Processing**: Ancileo handles payment, policy issuance, and confirmation

## Configuration

Requires `ANCILEO_API_KEY` in `.env` file:
```bash
ANCILEO_API_KEY=your_ancileo_api_key_here
```

## Fallback Behavior

- If Ancileo API key is not set: System uses only local policies
- If Ancileo API fails: System falls back to local quote generation
- User experience is uninterrupted - they always get insurance options

## Summary

**Ancileo enhances the system by:**
- ✅ Adding more insurance options beyond local policies
- ✅ Providing real-time, dynamic pricing
- ✅ Enabling complete purchase automation
- ✅ Expanding the insurance marketplace available to users

**It does NOT replace local policies** - it supplements them, giving users more choices and better pricing options.

