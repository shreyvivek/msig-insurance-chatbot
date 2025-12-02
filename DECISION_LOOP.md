# System Decision Loop - Architecture & Code Locations

## Overview
The WanderSure system uses a multi-stage decision loop to process user queries and provide intelligent, personalized responses. This document maps out the decision flow and where to find each component.

---

## Main Entry Point

### **File**: `run_server.py`
### **Function**: `@app.post("/api/ask")` (Line 139)

This is where ALL user questions enter the system.

```python
@app.post("/api/ask")
async def ask_question(request: dict):
    """Handle user questions with comprehensive error handling"""
```

**Location**: `/run_server.py:139-996`

---

## Decision Loop Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. USER QUESTION RECEIVED                                  │
│     Entry: /api/ask (run_server.py:139)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. PRE-PROCESSING & CONTEXT GATHERING                      │
│     - Extract question text                                  │
│     - Get user_id, context_data                              │
│     - Check for destination mentions                         │
│     Location: run_server.py:142-181                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. DESTINATION & CLAIMS ANALYSIS                           │
│     Decision: Is a destination mentioned?                    │
│     Location: run_server.py:182-238                          │
│                                                              │
│     If YES:                                                  │
│       → claims_analyzer.analyze_destination_and_recommend()  │
│       → Adds claims data to enhanced_context                 │
│       File: claims_analyzer.py                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. QUESTION TYPE DETECTION                                 │
│     Location: run_server.py:481-996                          │
│                                                              │
│     Multiple parallel checks:                                │
│                                                              │
│     a) ACTIVITY COVERAGE QUESTION?                          │
│        Pattern: "does [policy] cover [activity]?"           │
│        → ActivityPolicyMatcher                              │
│        Location: run_server.py:481-553                       │
│        File: activity_policy_matcher.py                      │
│                                                              │
│     b) CANCELLATION/REFUND QUESTION?                        │
│        Keywords: cancel, refund, cooling-off                │
│        → Adds cancellation context                          │
│        Location: run_server.py:557-584                       │
│                                                              │
│     c) POLICY COMPARISON QUESTION?                          │
│        Keywords: compare, difference, vs                    │
│        → Policy Intelligence comparison                     │
│        Location: run_server.py:587-589                       │
│        File: policy_intelligence.py                          │
│                                                              │
│     d) PRICING/PREMIUM QUESTION?                            │
│        Keywords: premium, price, cost, fee                  │
│        → Pricing calculator                                 │
│        Location: run_server.py:585                           │
│        File: pricing_calculator.py                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. USER CONTEXT BUILDING                                   │
│     Location: run_server.py:639-730                          │
│                                                              │
│     - Extract user_data from localStorage                    │
│     - Extract purchased_insurance data                       │
│     - Build user_context string with:                       │
│       • User profile & onboarding data                       │
│       • Purchased insurance details                          │
│       • Trip details                                         │
│                                                              │
│     Critical for personalization!                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. CONVERSATION HANDLER                                    │
│     File: conversation_handler.py                            │
│     Function: handle_question() (Line 101)                   │
│                                                              │
│     This is the CORE AI processing:                         │
│                                                              │
│     a) Question Analysis (Lines 128-140):                   │
│        - is_travel_question?                                 │
│        - is_insurance_question?                              │
│        - has_claims_data?                                    │
│                                                              │
│     b) Context Building (Lines 142-265):                    │
│        - User memory                                         │
│        - Sentiment detection                                 │
│        - Language detection                                  │
│        - Role-based personality                              │
│                                                              │
│     c) LLM Processing (Lines 350-450):                      │
│        - Builds comprehensive prompt                         │
│        - Calls Groq LLM (llama-3.3-70b-versatile)           │
│        - Formats response                                    │
│                                                              │
│     Location: conversation_handler.py:101-448                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  7. RESPONSE FORMATTING & ENHANCEMENT                       │
│     Location: conversation_handler.py:400-448                │
│                                                              │
│     - Cleans image tags                                      │
│     - Adds suggested questions                               │
│     - Formats for frontend                                   │
│                                                              │
│     Returns structured dict:                                │
│     {                                                         │
│       "answer": str,                                         │
│       "content": str,                                        │
│       "message": str,                                        │
│       "suggested_questions": List,                           │
│       "quotes": List,                                        │
│       ...                                                    │
│     }                                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  8. POST-PROCESSING IN /api/ask                             │
│     Location: run_server.py:760-780                          │
│                                                              │
│     - Adds claims_analysis to response (if available)        │
│     - Enhances answer/content with claims summary            │
│     - Returns final response                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  9. FRONTEND RENDERING                                      │
│     File: frontend/app/page.tsx                              │
│     Function: handleSend() (Line 2902)                       │
│                                                              │
│     - Receives response from /api/ask                        │
│     - Adds message to chat                                   │
│     - Renders with EnhancedMarkdown component                │
│     - Shows quotes, suggested questions, etc.                │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Decision Points

### 1. **Destination Detection** 
**Location**: `run_server.py:164-177`

Checks if user mentions a destination in their question:
```python
destination_keywords = ["chennai", "coimbatore", "india", ...]
for dest in destination_keywords:
    if dest.lower() in question_lower:
        destination_mentioned = dest
        break
```

**If destination found** → Triggers claims analysis before normal flow

---

### 2. **Question Type Classification**
**Location**: `run_server.py:481-589`

The system checks for specific question patterns:

#### a) Activity Coverage Questions
```python
is_activity_coverage_question = any(keyword in question_lower for keyword in [
    "cover", "coverage", "does", "will", "include", ...
])
```
**File**: `activity_policy_matcher.py`

#### b) Cancellation Questions
```python
cancellation_keywords = ["cancel", "cancellation", "refund", ...]
is_cancellation_question = any(keyword in question_lower_check for keyword in cancellation_keywords)
```
**Location**: `run_server.py:557-584`

#### c) Comparison Questions
```python
is_comparison_question = any(keyword in question_lower_check for keyword in 
    ["compare", "difference", "vs", "versus", ...])
```

---

### 3. **Insurance vs Travel Question**
**Location**: `conversation_handler.py:127-140`

```python
is_travel_question = self._is_travel_question(question)
is_insurance_question = self._is_insurance_question(question)
has_claims_data = context and ("CLAIMS DATA" in context)
```

**Method locations**:
- `_is_travel_question()`: `conversation_handler.py:152`
- `_is_insurance_question()`: `conversation_handler.py:162`

---

### 4. **Role-Based Personality**
**Location**: `conversation_handler.py:106-110`

```python
current_role = self.user_roles.get(user_id, "travel_agent")
role_config = self.roles.get(current_role, self.roles["travel_agent"])
```

**Available roles**: Defined in `conversation_handler.py:23-82`

---

## Intelligence Modules

### **Block 1: Policy Intelligence**
**File**: `policy_intelligence.py`
**Purpose**: Analyze policy documents, compare policies, explain coverage

**Key Methods**:
- `compare_policies()`: Compare multiple policies on criteria
- `explain_coverage()`: Explain specific coverage topics
- `check_eligibility()`: Check if user is eligible for policy

**Used in**: `run_server.py:481-996`, `intelligent_recommender.py`

---

### **Block 2: Conversational Intelligence**
**File**: `conversation_handler.py`
**Purpose**: Handle natural language conversations, role-based responses

**Key Methods**:
- `handle_question()`: Main conversation handler
- `_is_travel_question()`: Detect travel-related questions
- `_is_insurance_question()`: Detect insurance-related questions

**Used in**: `run_server.py:735-780`

---

### **Block 3: Document Intelligence**
**File**: `document_intelligence.py`
**Purpose**: Extract trip details from uploaded documents (itineraries, etc.)

**Key Methods**:
- `extract_trip_info()`: Extract structured data from documents

**Used in**: `/api/upload` endpoint (not in main decision loop, but provides context)

---

### **Block 4: Claims Analysis (Predictive Intelligence)**
**File**: `claims_analyzer.py`
**Purpose**: Analyze historical claims data for destinations

**Key Methods**:
- `analyze_destination_and_recommend()`: Get claims insights for destination

**Used in**: `run_server.py:195-238` (when destination is mentioned)

---

### **Block 5: Predictive Intelligence**
**File**: `predictive_intelligence.py`
**Purpose**: Risk assessment, predictive insights

**Key Methods**:
- `get_risk_assessment()`: Assess risk for trip
- `predict_premium()`: Predict insurance premium

**Used in**: `intelligent_recommender.py` (for recommendations)

---

## Quote Generation Flow

### When user asks for quotes:
**Location**: `/api/quote` endpoint in `run_server.py`

1. **Ancileo API** (Primary source)
   - Location: `run_server.py:1649-1863`
   - File: `ancileo_api.py`

2. **Taxonomy Matching** (Fallback)
   - Location: `run_server.py:1864-2200`
   - File: `taxonomy_matcher.py`

3. **Policy Scoring**
   - Location: `run_server.py:410-479`
   - File: `policy_scorer.py`

---

## Error Handling Strategy

### **Location**: `run_server.py:733-996`

The system uses multiple layers of error handling:

1. **Try-Except around conversation handler** (Line 734)
   - Primary: `conversation.handle_question()`
   - Fallback: Simplified AI call
   - Final fallback: Generic helpful message

2. **Graceful degradation**:
   - If claims analysis fails → Continue without it
   - If policy comparison fails → Continue with basic response
   - Always returns SOME response to user

---

## Context Building Priority

### **Location**: `run_server.py:639-730`

The system builds context in this order:

1. **Enhanced context** (claims data, special question context)
2. **User profile data** (from localStorage)
3. **Purchased insurance data** (from localStorage)
4. **Trip details** (if available)

**Critical**: User context is ALWAYS built, even if empty, to ensure personalization attempts.

---

## Key Files Reference

| Component | File | Key Functions |
|-----------|------|---------------|
| **Main Entry Point** | `run_server.py` | `ask_question()` (line 139) |
| **Conversation Handler** | `conversation_handler.py` | `handle_question()` (line 101) |
| **Claims Analysis** | `claims_analyzer.py` | `analyze_destination_and_recommend()` |
| **Policy Intelligence** | `policy_intelligence.py` | `compare_policies()`, `explain_coverage()` |
| **Activity Matcher** | `activity_policy_matcher.py` | `compare_policies_for_activity()` |
| **Intelligent Recommender** | `intelligent_recommender.py` | `recommend_policies()` |
| **Frontend** | `frontend/app/page.tsx` | `handleSend()` (line 2902) |

---

## Decision Tree Summary

```
User Question
    │
    ├─→ Has destination? → Claims Analysis → Enhanced Context
    │
    ├─→ Activity coverage? → ActivityPolicyMatcher → Direct Response
    │
    ├─→ Cancellation? → Add cancellation context → AI Processing
    │
    ├─→ Comparison? → Policy Intelligence → AI Processing
    │
    └─→ General Question → 
            │
            ├─→ Build User Context (profile, purchased insurance)
            │
            ├─→ Conversation Handler
            │   ├─→ Detect question type (travel/insurance)
            │   ├─→ Build prompt with context
            │   └─→ LLM Processing
            │
            └─→ Format & Return Response
```

---

## Quick Code Navigation

**To understand the full flow**, start here:
1. `run_server.py:139` - Entry point
2. `run_server.py:182-238` - Destination/claims detection
3. `run_server.py:481-996` - Question type routing
4. `run_server.py:639-730` - User context building
5. `conversation_handler.py:101` - Core AI processing
6. `conversation_handler.py:350-450` - LLM call and response

**For specific features**:
- Claims analysis: `claims_analyzer.py`
- Policy comparison: `policy_intelligence.py`
- Activity matching: `activity_policy_matcher.py`
- Frontend rendering: `frontend/app/page.tsx`

---

## Tips for Modifying the Decision Loop

1. **To add a new question type**: 
   - Add detection in `run_server.py:481-589`
   - Create handler function
   - Add route before conversation handler

2. **To modify context building**:
   - Edit `run_server.py:639-730` (user context)
   - Edit `conversation_handler.py:142-265` (conversation context)

3. **To change AI behavior**:
   - Modify prompts in `conversation_handler.py:267-340`
   - Adjust role configs in `conversation_handler.py:23-82`

4. **To add new intelligence module**:
   - Create new file (e.g., `new_intelligence.py`)
   - Import in `run_server.py`
   - Call from appropriate decision point

---

**Last Updated**: Based on current codebase structure
**Main Entry Point**: `/api/ask` endpoint in `run_server.py:139`

