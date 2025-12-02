# Context Retrieval System - Detailed Documentation

## Overview
The WanderSure system uses a multi-layered context retrieval mechanism to build personalized, context-aware responses. Context is gathered from multiple sources and combined into a comprehensive context string that guides the AI's responses.

---

## Context Retrieval Flow

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND: localStorage Data Collection                     │
│  Location: frontend/app/page.tsx:2845-3000                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND: Data Retrieval from localStorage                 │
│  - wandersure_user_data                                     │
│  - wandersure_purchased_insurance                           │
│  Location: frontend/app/page.tsx:2950-2970                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND: Request Receipt                                   │
│  Location: run_server.py:639-641                            │
│  - user_data from request                                   │
│  - purchased_insurance from request                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND: Context Building                                  │
│  Location: run_server.py:647-730                            │
│  - User Profile Context                                     │
│  - Purchased Insurance Context                              │
│  - Enhanced Context (claims, special questions)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CONVERSATION HANDLER: Additional Context                   │
│  Location: conversation_handler.py:124-157                  │
│  - User Memory (session-based)                              │
│  - Conversation History                                     │
│  - Sentiment & Language                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  FINAL CONTEXT STRING                                       │
│  Combined and sent to LLM                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Context Sources

### 1. **User Onboarding Data (localStorage)**
**Storage Key**: `wandersure_user_data`  
**Location**: `frontend/app/page.tsx:2950-2970`

#### Data Structure:
```typescript
{
  name: string,
  email: string,
  phone: string,
  date_of_birth: string,
  age: number,
  interests: string[],
  medical_conditions: string[],
  passport_number: string,
  nric_number: string
}
```

#### Frontend Retrieval:
```typescript
// Location: frontend/app/page.tsx:2950-2970
const savedUserData = localStorage.getItem('wandersure_user_data')
if (savedUserData) {
  const userData = JSON.parse(savedUserData)
  // Send to backend in request
}
```

#### Backend Processing:
**Location**: `run_server.py:649-667`

```python
if user_data and isinstance(user_data, dict) and len(user_data) > 0:
    user_context += "\n\n👤 USER PROFILE & ONBOARDING DATA:\n"
    if user_data.get("name"):
        user_context += f"- Name: {user_data.get('name')}\n"
    if user_data.get("email"):
        user_context += f"- Email: {user_data.get('email')}\n"
    if user_data.get("phone"):
        user_context += f"- Phone: {user_data.get('phone')}\n"
    if user_data.get("date_of_birth") or user_data.get("age"):
        dob_or_age = user_data.get('date_of_birth') or f"Age {user_data.get('age')}"
        user_context += f"- Age/DOB: {dob_or_age}\n"
    if user_data.get("interests"):
        user_context += f"- Travel Interests: {', '.join(user_data.get('interests', []))}\n"
    if user_data.get("medical_conditions"):
        user_context += f"- Medical Conditions: {', '.join(user_data.get('medical_conditions', []))}\n"
    if user_data.get("passport_number"):
        user_context += f"- Passport: {user_data.get('passport_number')}\n"
    if user_data.get("nric_number"):
        user_context += f"- NRIC: {user_data.get('nric_number')}\n"
```

---

### 2. **Purchased Insurance Data (localStorage)**
**Storage Key**: `wandersure_purchased_insurance`  
**Location**: `frontend/app/page.tsx:2851-2860`

#### Data Structure:
```typescript
{
  plan_name: string,           // Policy name (e.g., "Scootsurance")
  policy_number: string,       // Policy number from Ancileo
  purchase_id: string,         // Purchase ID from Ancileo
  purchase_date: string,       // ISO date string
  amount: number,              // Purchase amount
  currency: string,            // Currency code
  source: string,              // "ancileo" or "local"
  trip_details: {              // Trip information
    destination: string,
    departure_date: string,
    return_date: string,
    travelers: number
  },
  insureds: Array<{            // Insured travelers
    name: string,
    age: number,
    email: string,
    phone: string
  }>,
  ancileo_purchase_data: {}    // Full Ancileo response
}
```

#### Frontend Retrieval:
**Location**: `frontend/app/page.tsx:2851-2860`

```typescript
const savedPurchasedInsurance = localStorage.getItem('wandersure_purchased_insurance')
if (savedPurchasedInsurance) {
  const purchasedInsurance = JSON.parse(savedPurchasedInsurance)
  // Send to backend in request
}
```

#### Backend Processing:
**Location**: `run_server.py:669-725`

```python
if purchased_insurance and isinstance(purchased_insurance, dict) and len(purchased_insurance) > 0:
    user_context += "\n\n🛡️ PURCHASED INSURANCE:\n"
    
    # Extract plan_name as string (handle object cases)
    plan_name = purchased_insurance.get("plan_name")
    if plan_name:
        # Convert to string if it's an object
        if isinstance(plan_name, dict):
            plan_name = plan_name.get("name") or plan_name.get("plan_name") or str(plan_name)
        elif not isinstance(plan_name, str):
            plan_name = str(plan_name)
        plan_name = str(plan_name).strip()
        if plan_name and plan_name != "None" and plan_name.lower() != "null":
            user_context += f"- Policy: **{plan_name}**\n"
            # Add instruction for AI to use exact name
            user_context += f"- IMPORTANT: When referencing this policy, use the exact policy name string: \"{plan_name}\"\n"
    
    # Policy number
    policy_number = purchased_insurance.get("policy_number")
    if policy_number:
        user_context += f"- Policy Number: {policy_number}\n"
    
    # Purchase date
    purchase_date = purchased_insurance.get("purchase_date")
    if purchase_date:
        user_context += f"- Purchase Date: {purchase_date}\n"
    
    # Trip details
    if purchased_insurance.get("trip_details"):
        trip = purchased_insurance.get("trip_details", {})
        if isinstance(trip, dict):
            destination = trip.get("destination")
            if destination:
                user_context += f"- Trip Destination: {destination}\n"
            departure = trip.get("departure_date")
            if departure:
                user_context += f"- Departure: {departure}\n"
            return_date = trip.get("return_date")
            if return_date:
                user_context += f"- Return: {return_date}\n"
    
    # Insured travelers
    if purchased_insurance.get("insureds"):
        insured_names = []
        for insured in purchased_insurance.get("insureds", []):
            if isinstance(insured, dict):
                name = insured.get("name") or f"{insured.get('firstName', '')} {insured.get('lastName', '')}".strip()
                if name:
                    insured_names.append(str(name))
        if insured_names:
            user_context += f"- Insured Travelers: {', '.join(insured_names)}\n"
```

---

### 3. **Enhanced Context (Question-Specific)**
**Location**: `run_server.py:180-238, 570-583`

#### A. Claims Analysis Context
**When**: Destination mentioned in question  
**Location**: `run_server.py:182-238`

```python
if destination_mentioned:
    claims_analysis = await claims_analyzer.analyze_destination_and_recommend(
        destination=destination_mentioned,
        trip_duration=trip_duration
    )
    
    if claims_analysis.get("has_data"):
        claims_context = f"""
🎯 CLAIMS DATA FOR {destination_mentioned.upper()}:
Total historical claims analyzed: {claims_analysis.get('total_claims', 0)}
Risk summary: {claims_analysis.get('risk_summary', '')}
Common incidents: {common_incidents_str}
Top claim type: {top_rec.get('claim_type', 'N/A')} 
- Incidence rate: {top_rec.get('incidence_rate', 'N/A')}
- Average cost per claim: ${top_rec.get('average_cost', 0):,.2f} SGD
- Recommended coverage: ${top_rec.get('recommended_coverage', 0):,.2f} SGD

CRITICAL INSTRUCTION: 
1. You MUST prominently feature this claims data at the START of your response
2. Use the EXACT format: "In {destination}, {incidence_rate} of travelers have claimed..."
3. ALWAYS ask: "Would you like to purchase insurance to specifically cover this?"
"""
        enhanced_context = enhanced_context + claims_context
```

#### B. Cancellation Question Context
**When**: Cancellation/refund question detected  
**Location**: `run_server.py:567-583`

```python
if is_cancellation_question:
    enhanced_context = enhanced_context + """
📋 CANCELLATION QUESTION DETECTED:

The user is asking about canceling their policy. Important instructions:
1. If the user has PURCHASED INSURANCE, reference THEIR specific policy
2. Provide cancellation steps, requirements, refund policies
3. Use policy intelligence to fetch exact cancellation terms
4. Mention cooling-off periods, refund eligibility, and fees
"""
```

---

### 4. **Conversation Handler Context**
**Location**: `conversation_handler.py:124-157`

#### A. User Memory (Session-Based)
**Storage**: In-memory dictionary (`self.memory`)  
**Location**: `conversation_handler.py:67-69`

```python
def get_user_memory(self, user_id: str) -> Dict:
    """Get user's conversation memory"""
    return self.memory.get(user_id, {})
```

**Memory Structure**:
```python
{
    "preferences": {...},           # User preferences
    "trip_details": {...},          # Mentioned trip details
    "last_trip": {...},             # Last trip mentioned
    "recent_conversation": [        # Last 6 messages
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ],
    "last_updated": "2025-01-01T00:00:00"
}
```

#### B. Context Building in Conversation Handler
**Location**: `conversation_handler.py:142-157`

```python
# Build rich context
context_parts = []

if user_memory.get("preferences"):
    context_parts.append(f"User preferences: {user_memory['preferences']}")

if user_memory.get("trip_details"):
    context_parts.append(f"User's trip: {user_memory['trip_details']}")

if user_memory.get("last_trip"):
    context_parts.append(f"Last trip: {user_memory['last_trip']}")

if context:  # Context from backend (user_data, purchased_insurance, etc.)
    context_parts.append(f"Additional context: {context}")

full_context = "\n".join(context_parts) if context_parts else "No previous context"
```

#### C. Conversation History
**Location**: `conversation_handler.py:379-383`

```python
# Add recent conversation history if available
if user_memory.get("recent_conversation"):
    recent = user_memory["recent_conversation"][-4:]  # Last 4 exchanges
    for msg in recent:
        conversation_messages.insert(-1, msg)  # Insert before final user message
```

**Storage**: After each response (Lines 397-408)
```python
# Store conversation history (last 6 messages)
if not user_memory.get("recent_conversation"):
    user_memory["recent_conversation"] = []

user_memory["recent_conversation"].append({"role": "user", "content": question})
user_memory["recent_conversation"].append({"role": "assistant", "content": answer_text[:500]})

# Keep only last 6 messages
if len(user_memory["recent_conversation"]) > 6:
    user_memory["recent_conversation"] = user_memory["recent_conversation"][-6:]

self.memory[user_id] = user_memory
```

---

### 5. **Sentiment & Language Detection**
**Location**: `conversation_handler.py:117-122`

```python
# Detect language if not provided
if not language:
    language = self.multilingual.detect_language(question)

# Detect sentiment
sentiment = self._detect_sentiment(question)
```

**Used in**: Tone adaptation in system prompt (Lines 159-166)

---

## Complete Context String Structure

### Final Context Format:
```
[Enhanced Context] (claims data, special questions)
+
[User Profile Context] (from localStorage)
+
[Purchased Insurance Context] (from localStorage)
+
[Conversation Memory] (session-based)
+
[Conversation History] (last 4 exchanges)
```

### Example Final Context:
```
🎯 CLAIMS DATA FOR INDIA:
Total historical claims analyzed: 150
Risk summary: Medium risk destination
Top claim type: Medical expenses
- Incidence rate: 45%
- Average cost: $1,500 SGD

👤 USER PROFILE & ONBOARDING DATA:
- Name: John Doe
- Email: john@example.com
- Travel Interests: Adventure, Food, Culture
- Medical Conditions: None

🛡️ PURCHASED INSURANCE:
- Policy: **Scootsurance**
- Policy Number: 870000001-18589
- Purchase Date: 2025-11-30T10:00:00Z
- Trip Destination: Coimbatore
- Departure: 2025-12-06
- Return: 2026-01-15
- Insured Travelers: John Doe, Jane Doe

Additional context: User preferences: adventure travel, last trip: Japan 2024
```

---

## Frontend Context Retrieval Flow

### Location: `frontend/app/page.tsx:2845-3000`

#### Step 1: Retrieve from localStorage
```typescript
// Location: frontend/app/page.tsx:2950-2970
const handleSend = async () => {
  // ... question processing ...
  
  // ALWAYS get user onboarding data from localStorage
  let userData = null
  try {
    const savedUserData = localStorage.getItem('wandersure_user_data')
    if (savedUserData) {
      userData = JSON.parse(savedUserData)
      console.log('✅ Retrieved user onboarding data:', {
        name: userData?.name,
        hasInterests: !!userData?.interests,
        hasMedicalConditions: !!userData?.medical_conditions
      })
    }
  } catch (e) {
    console.error('Error parsing user data:', e)
  }
  
  // ALWAYS get purchased insurance data
  let purchasedInsurance = null
  try {
    const savedPurchasedInsurance = localStorage.getItem('wandersure_purchased_insurance')
    if (savedPurchasedInsurance) {
      purchasedInsurance = JSON.parse(savedPurchasedInsurance)
      console.log('✅ Retrieved purchased insurance:', {
        policyName: purchasedInsurance?.plan_name,
        policyNumber: purchasedInsurance?.policy_number
      })
    }
  } catch (e) {
    console.error('Error parsing purchased insurance:', e)
  }
```

#### Step 2: Include in Request
```typescript
// Location: frontend/app/page.tsx:2975-2988
const response = await fetch(`${API_URL}/api/ask`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: input,
    user_id: 'default_user',
    language: language,
    context_data: {
      trip_details: contextData.trip_details || null
    },
    user_data: userData,              // ← User onboarding data
    purchased_insurance: purchasedInsurance  // ← Purchased insurance
  })
})
```

---

## Backend Context Processing

### Location: `run_server.py:639-730`

#### Step 1: Extract from Request
```python
# Location: run_server.py:639-641
user_data = request.get("user_data") or {}  # From frontend localStorage
purchased_insurance = request.get("purchased_insurance") or {}  # From localStorage

# Log for debugging
logger.info(f"📋 [CONTEXT] User data: name={bool(user_data.get('name'))}, hasData={bool(user_data)}")
logger.info(f"🛡️ [CONTEXT] Purchased insurance: policy={purchased_insurance.get('plan_name', 'N/A')}")
```

#### Step 2: Build User Context String
```python
# Location: run_server.py:647-725
user_context = ""

# Build user profile section
if user_data and isinstance(user_data, dict) and len(user_data) > 0:
    user_context += "\n\n👤 USER PROFILE & ONBOARDING DATA:\n"
    # ... add all user fields ...

# Build purchased insurance section
if purchased_insurance and isinstance(purchased_insurance, dict) and len(purchased_insurance) > 0:
    user_context += "\n\n🛡️ PURCHASED INSURANCE:\n"
    # ... add all insurance fields ...
```

#### Step 3: Combine All Context
```python
# Location: run_server.py:727-730
final_context = enhanced_context if enhanced_context else request.get("context", "")
if user_context:
    final_context = final_context + user_context

# Pass to conversation handler
result = await conversation.handle_question(
    question=request.get("question"),
    context=final_context,  # ← Combined context
    ...
)
```

---

## Conversation Handler Context Processing

### Location: `conversation_handler.py:124-157, 379-383`

#### Step 1: Get User Memory
```python
# Location: conversation_handler.py:124-125
user_memory = self.get_user_memory(user_id)  # Session-based memory
```

#### Step 2: Build Context Parts
```python
# Location: conversation_handler.py:142-157
context_parts = []

if user_memory.get("preferences"):
    context_parts.append(f"User preferences: {user_memory['preferences']}")

if user_memory.get("trip_details"):
    context_parts.append(f"User's trip: {user_memory['trip_details']}")

if context:  # This is the final_context from backend (includes user_data, purchased_insurance)
    context_parts.append(f"Additional context: {context}")

full_context = "\n".join(context_parts) if context_parts else "No previous context"
```

#### Step 3: Add Conversation History
```python
# Location: conversation_handler.py:379-383
conversation_messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

# Add recent conversation history
if user_memory.get("recent_conversation"):
    recent = user_memory["recent_conversation"][-4:]  # Last 4 exchanges
    for msg in recent:
        conversation_messages.insert(-1, msg)  # Insert before final user message
```

---

## Context Storage Locations

### Frontend (localStorage)
| Key | Purpose | Structure |
|-----|---------|-----------|
| `wandersure_user_data` | User onboarding/profile data | UserProfile object |
| `wandersure_purchased_insurance` | Purchased insurance details | PurchasedInsurance object |
| `wandersure_conversation_threads` | Chat history threads | Array of ConversationThread |
| `wandersure_thread_{threadId}` | Messages for specific thread | Array of Message |

### Backend (In-Memory)
| Storage | Purpose | Location |
|---------|---------|----------|
| `self.memory` | Session-based user memory | `conversation_handler.py:24` |
| `self.user_roles` | User role preferences | `conversation_handler.py` |
| `self.conversation_count` | Conversation counter | `conversation_handler.py` |

---

## Context Priority & Merging

### Priority Order:
1. **Enhanced Context** (claims data, special questions) - Highest priority
2. **User Profile Context** (from localStorage)
3. **Purchased Insurance Context** (from localStorage)
4. **Conversation Memory** (session-based)
5. **Conversation History** (last 4 exchanges)

### Merging Logic:
```python
# Location: run_server.py:727-730
final_context = enhanced_context if enhanced_context else request.get("context", "")
if user_context:  # User profile + purchased insurance
    final_context = final_context + user_context

# Then in conversation_handler.py:154
if context:  # final_context from backend
    context_parts.append(f"Additional context: {context}")

full_context = "\n".join(context_parts)
```

---

## Key Functions Reference

| Function | Location | Purpose |
|----------|----------|---------|
| `handleSend()` | `frontend/app/page.tsx:2902` | Frontend: Retrieves localStorage data and sends to backend |
| `ask_question()` | `run_server.py:139` | Backend: Receives request, builds user context |
| `get_user_memory()` | `conversation_handler.py:67` | Gets session-based user memory |
| `handle_question()` | `conversation_handler.py:101` | Core: Processes question with full context |
| `update_memory()` | `conversation_handler.py:60` | Updates user memory with new data |

---

## Context Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  localStorage (Browser)                                      │
│  ├─ wandersure_user_data                                    │
│  └─ wandersure_purchased_insurance                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Frontend Retrieval (page.tsx:2950-2970)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  HTTP Request to /api/ask                                   │
│  {                                                           │
│    question: "...",                                          │
│    user_data: {...},           ← From localStorage          │
│    purchased_insurance: {...}  ← From localStorage          │
│  }                                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Backend Processing (run_server.py:639-730)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Context String Building                                    │
│  ├─ Enhanced Context (claims, special questions)            │
│  ├─ User Profile Context (from user_data)                  │
│  └─ Purchased Insurance Context (from purchased_insurance) │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Pass to Conversation Handler
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Conversation Handler (conversation_handler.py:101)        │
│  ├─ Get User Memory (session-based)                        │
│  ├─ Add Conversation History (last 4 exchanges)            │
│  └─ Combine with full_context                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Build Final Prompt
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  LLM Prompt with Full Context                               │
│  {                                                           │
│    system: "...",                                           │
│    user: "Question + Full Context String"                   │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Important Notes

### 1. **ALWAYS Retrieve Context**
- Frontend ALWAYS retrieves user_data and purchased_insurance from localStorage
- Backend ALWAYS builds user_context, even if empty
- This ensures personalization attempts even with missing data

### 2. **Type Safety**
- All policy names are converted to strings (never objects)
- All dates are normalized to ISO format
- All lists are validated before joining

### 3. **Error Handling**
- If localStorage parse fails → Continue with empty data
- If context building fails → Continue with available data
- Always logs context availability for debugging

### 4. **Context Persistence**
- localStorage persists across browser sessions
- Session memory (conversation_handler.memory) is in-memory only
- Conversation history is stored in localStorage per thread

---

## Debugging Context Issues

### Log Locations:

1. **Frontend Logs**:
   - `frontend/app/page.tsx:2956-2963` - User data retrieval
   - `frontend/app/page.tsx:2856-2860` - Purchased insurance retrieval

2. **Backend Logs**:
   - `run_server.py:644-645` - User data availability
   - `run_server.py:645` - Purchased insurance availability
   - `conversation_handler.py:137-138` - Claims data detection

### Common Issues:

1. **Missing user_data**: Check localStorage key `wandersure_user_data`
2. **Missing purchased_insurance**: Check localStorage key `wandersure_purchased_insurance`
3. **[object Object] in responses**: Ensure policy names are strings (fixed in run_server.py:672-684)
4. **No personalization**: Verify context is being built (check logs at run_server.py:644-645)

---

## Code Files Reference

| Component | File | Key Lines |
|-----------|------|-----------|
| **Frontend Retrieval** | `frontend/app/page.tsx` | 2845-3000 |
| **Backend Context Building** | `run_server.py` | 639-730 |
| **Conversation Memory** | `conversation_handler.py` | 124-157, 379-408 |
| **Context Storage** | `conversation_handler.py` | 24, 67-69 |
| **Claims Analysis** | `run_server.py` | 182-238 |
| **Purchased Insurance Storage** | `frontend/app/page.tsx` | 3885-3897 |

---

**Last Updated**: Based on current codebase structure  
**Key Principle**: Context is ALWAYS built, even if empty, to ensure consistent personalization attempts




