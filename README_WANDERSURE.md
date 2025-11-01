# 🧳 WanderSure - Your Smart Travel Insurance Companion

> "As easy as chatting with a travel buddy who just happens to know everything about insurance."

## 🎯 What is WanderSure?

WanderSure is a **complete conversational AI system** that transforms travel insurance from boring form-filling into an engaging, intelligent dialogue. It's a fully functional implementation of all 5 innovation blocks with creative enhancements.

## ✨ Key Features

### 🧠 Block 1: Policy Intelligence
- Extracts and normalizes insurance policies from PDFs
- Compares policies side-by-side with citations
- Explains coverage in natural language
- Checks eligibility automatically

### 💬 Block 2: Conversational Magic
- Natural language Q&A with emotional intelligence
- Detects sentiment and adapts tone
- Multi-language support
- Conversation memory and context awareness

### 📄 Block 3: Document Intelligence
- Extracts trip details from bookings/itineraries
- Generates personalized quotes instantly
- Activity-based pricing adjustments
- Intelligent validation and clarification

### 💳 Block 4: Seamless Commerce
- Stripe payment integration
- In-chat payment experience
- Real-time status tracking
- DynamoDB integration

### 🎯 Block 5: Predictive Intelligence
- Risk assessment based on claims data
- Personalized coverage recommendations
- Activity-based risk scoring
- Seasonal pattern analysis

## 🚀 Quick Start

### 1. Install Dependencies

**On macOS (use `pip3` and `python3`):**
```bash
pip3 install -r requirements.txt
```

**On Linux/Windows:**
```bash
pip install -r requirements.txt
```

**Or use the macOS script:**
```bash
./start_mac.sh
```

### 2. Set Environment Variables
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Run Server

**On macOS:**
```bash
python3 run_server.py
```

**On Linux/Windows:**
```bash
python run_server.py
```

Server runs on http://localhost:8001

### 4. Run Frontend (Optional)
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

## 📖 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[WANDERSURE_FEATURES.md](WANDERSURE_FEATURES.md)** - Complete feature list
- **[README_IMPLEMENTATION.md](README_IMPLEMENTATION.md)** - Technical details

## 🎨 Try It Out

### Via Web Interface
1. Start the server: `python run_server.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000
4. Start chatting!

### Via API
```bash
curl -X POST http://localhost:8001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is travel insurance?"}'
```

### Example Questions
- "Compare medical coverage between TravelEasy and Scootsurance"
- "I'm traveling to Japan next week for skiing - what do you recommend?"
- "What does trip cancellation cover?"
- "I'm 72 years old - can I buy this?"
- "If my flight is cancelled due to weather, am I covered?"

## 🏗️ Architecture

```
User Input
    ↓
Frontend (Next.js) / MCP Client
    ↓
WanderSure Server (FastAPI/MCP)
    ↓
┌─────────────────────────────────────┐
│  Policy Intelligence                │
│  Conversation Handler                │
│  Document Intelligence              │
│  Payment Handler                    │
│  Predictive Intelligence            │
└─────────────────────────────────────┘
    ↓
Groq LLM (llama-3.3-70b-versatile)
    ↓
Stripe / DynamoDB / Policy PDFs
```

## 🔧 Technology Stack

- **Backend**: Python, FastAPI, MCP Protocol
- **AI**: Groq (llama-3.3-70b-versatile)
- **PDF Processing**: PyPDF2, pdfplumber
- **Payments**: Stripe, DynamoDB
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_system.py
```

## 📊 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/ask` | Ask questions |
| `POST /api/extract` | Extract trip info |
| `POST /api/quote` | Generate quotes |
| `POST /api/compare` | Compare policies |
| `POST /api/risk` | Risk assessment |
| `POST /api/payment/create` | Create payment |
| `GET /api/payment/status/{id}` | Check payment |

## 🌟 Innovation Highlights

1. **Dynamic Learning**: System learns insurance terminology on the fly
2. **Emotional Intelligence**: Adapts tone based on user sentiment
3. **Predictive Risk**: Multi-factor risk scoring with claims data
4. **Zero-Form Experience**: Extract everything from documents
5. **In-Chat Payments**: Seamless payment without redirects

## 📁 Project Structure

```
ancileo-msig/
├── wandersure_server.py         # MCP server
├── run_server.py                # FastAPI server
├── policy_intelligence.py       # Block 1
├── conversation_handler.py      # Block 2
├── document_intelligence.py     # Block 3
├── payment_handler.py           # Block 4
├── predictive_intelligence.py   # Block 5
├── test_system.py               # Test suite
├── frontend/                     # Next.js UI
├── Payments/                     # Payment services
├── Policy_Wordings/             # Source PDFs
└── Taxonomy/                     # Taxonomy structure
```

## 🎯 Requirements Met

### ✅ All 5 Blocks Implemented
- [x] Block 1: Policy Intelligence
- [x] Block 2: Conversational Magic
- [x] Block 3: Document Intelligence
- [x] Block 4: Seamless Commerce
- [x] Block 5: Predictive Intelligence

### ✅ Innovation Criteria
- [x] Unique approach to understanding documents
- [x] Creative normalization beyond taxonomies
- [x] Innovative comparison methods
- [x] Unique personality users love
- [x] Natural conversation flows
- [x] Creative citation methods
- [x] Novel extraction approaches
- [x] Seamless payment experience
- [x] Novel insights from claims data
- [x] Breakthrough predictive models

## 🚧 Future Enhancements

- Extract claims data automatically from PDF
- Integrate with real pricing APIs
- Add policy document generation
- Multi-user authentication
- WhatsApp/Telegram bot integration
- Voice interface support

## 📝 License

Built for Ancileo × MSIG Hackathon

## 🤝 Support

For issues or questions, check the documentation files:
- `SETUP.md` - Setup help
- `WANDERSURE_FEATURES.md` - Feature details
- `README_IMPLEMENTATION.md` - Technical docs

---

**WanderSure** - Making travel insurance as easy as chatting with a friend! ✈️🧳

