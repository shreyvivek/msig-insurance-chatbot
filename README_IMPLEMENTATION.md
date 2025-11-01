# WanderSure - Implementation Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (for payments)
- Groq API key

### Setup Steps

1. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and STRIPE keys
```

3. **Start Payment Services** (Optional, for Block 4)
```bash
cd Payments
docker-compose up -d
```

4. **Run the Server**
```bash
python run_server.py
# Server runs on http://localhost:8001
```

5. **Run the Frontend** (in a new terminal)
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

## 📋 Feature Blocks Implementation

### Block 1: Policy Intelligence ✅
- **Location**: `policy_intelligence.py`
- **Features**:
  - Extracts text from PDF policies using PyPDF2/pdfplumber
  - Normalizes policies to taxonomy using Groq LLM
  - Compares policies side-by-side
  - Explains coverage with citations
  - Checks eligibility

### Block 2: Conversational Magic ✅
- **Location**: `conversation_handler.py`
- **Features**:
  - Natural language Q&A
  - Sentiment detection and adaptive tone
  - Multi-language support
  - Conversation memory
  - Personality traits

### Block 3: Document Intelligence ✅
- **Location**: `document_intelligence.py`
- **Features**:
  - Extracts trip info from PDFs/images
  - Generates personalized quotes
  - Validates and enriches data
  - Activity-based pricing

### Block 4: Seamless Commerce ✅
- **Location**: `payment_handler.py`
- **Features**:
  - Creates Stripe payment sessions
  - Integrates with DynamoDB
  - Checks payment status
  - Handles webhook updates

### Block 5: Predictive Intelligence ✅
- **Location**: `predictive_intelligence.py`
- **Features**:
  - Risk assessment based on claims data
  - Personalized coverage recommendations
  - Activity-based risk scoring
  - Seasonal pattern analysis

## 🎯 API Endpoints

All endpoints run on `http://localhost:8001`:

- `POST /api/ask` - Ask questions
- `POST /api/extract` - Extract trip info from documents
- `POST /api/quote` - Generate quotes
- `POST /api/compare` - Compare policies
- `POST /api/risk` - Get risk assessment
- `POST /api/payment/create` - Create payment
- `GET /api/payment/status/{payment_id}` - Check payment status

## 🧪 Testing

### Test Policy Extraction
```python
from policy_intelligence import PolicyIntelligence
pi = PolicyIntelligence()
data = pi.get_normalized_data()
print(data)
```

### Test Document Extraction
```python
from document_intelligence import DocumentIntelligence
di = DocumentIntelligence()
result = await di.extract_trip_info("base64_encoded_pdf", "pdf")
```

### Test Payment Flow
```bash
cd Payments
python test_payment_flow.py
```

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY` - Required for all AI features
- `STRIPE_SECRET_KEY` - Required for payments
- `STRIPE_WEBHOOK_SECRET` - Required for webhooks
- `DDB_ENDPOINT` - DynamoDB endpoint (default: http://localhost:8000)
- `AWS_REGION` - AWS region (default: ap-southeast-1)

## 📦 Project Structure

```
ancileo-msig/
├── wandersure_server.py       # Main MCP server
├── run_server.py              # FastAPI fallback server
├── policy_intelligence.py     # Block 1
├── conversation_handler.py    # Block 2
├── document_intelligence.py  # Block 3
├── payment_handler.py         # Block 4
├── predictive_intelligence.py # Block 5
├── frontend/                  # Next.js chat UI
├── Payments/                  # Payment services
├── Policy_Wordings/           # Source PDFs
└── Taxonomy/                  # Taxonomy structure
```

## 🎨 Frontend Features

- Beautiful gradient design
- Real-time chat interface
- Markdown support for responses
- Quick action buttons
- Mobile responsive

## 🔍 Troubleshooting

### PDF Extraction Issues
- Ensure PyPDF2 and pdfplumber are installed
- Check file permissions on Policy_Wordings/

### Groq API Errors
- Verify GROQ_API_KEY is set correctly
- Check API rate limits

### Payment Issues
- Ensure Docker services are running
- Verify Stripe keys are test keys
- Check DynamoDB is accessible on port 8000

## 🚀 Production Deployment

1. Set production environment variables
2. Use production Stripe keys
3. Set up proper DynamoDB (not local)
4. Configure email service for policy delivery
5. Deploy frontend to Vercel/Netlify
6. Deploy backend to AWS/Render

## 💡 Innovation Highlights

1. **Dynamic Learning**: System learns terminology on the fly
2. **Emotional Intelligence**: Adapts tone based on sentiment
3. **Predictive Risk**: Uses claims data for recommendations
4. **Zero-Form Experience**: Extract everything from documents
5. **In-Chat Payments**: Seamless payment without redirects

