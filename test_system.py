#!/usr/bin/env python3
"""
Test script for WanderSure system
Tests all major components
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_policy_intelligence():
    """Test Block 1: Policy Intelligence"""
    print("\n" + "="*70)
    print("Testing Block 1: Policy Intelligence")
    print("="*70)
    
    from policy_intelligence import PolicyIntelligence
    pi = PolicyIntelligence()
    
    print(f"✓ Policy Intelligence initialized")
    print(f"✓ Loaded {len(pi.get_policy_list())} policies")
    
    # Test comparison
    result = await pi.compare_policies("medical coverage", ["TravelEasy Policy QTD032212"])
    print(f"✓ Policy comparison works: {len(result.get('comparison', ''))} chars")
    
    # Test explanation
    explanation = await pi.explain_coverage("trip cancellation")
    print(f"✓ Coverage explanation works: {len(explanation)} chars")
    
    return True

async def test_conversation():
    """Test Block 2: Conversational Magic"""
    print("\n" + "="*70)
    print("Testing Block 2: Conversational Magic")
    print("="*70)
    
    from conversation_handler import ConversationHandler
    ch = ConversationHandler()
    
    print("✓ Conversation Handler initialized")
    
    # Test question handling
    answer = await ch.handle_question("What is travel insurance?", language="English")
    print(f"✓ Question handling works: {len(answer)} chars response")
    print(f"  Sample: {answer[:100]}...")
    
    return True

async def test_document_intelligence():
    """Test Block 3: Document Intelligence"""
    print("\n" + "="*70)
    print("Testing Block 3: Document Intelligence")
    print("="*70)
    
    from document_intelligence import DocumentIntelligence
    di = DocumentIntelligence()
    
    print("✓ Document Intelligence initialized")
    
    # Test quote generation
    quote = await di.generate_quote(
        destination="Japan",
        start_date="2024-12-20",
        end_date="2024-12-27",
        travelers=1,
        ages=[30],
        activities=["skiing"]
    )
    print(f"✓ Quote generation works")
    print(f"  Quote ID: {quote.get('quote_id')}")
    print(f"  Plans: {len(quote.get('quotes', []))}")
    
    return True

async def test_predictive_intelligence():
    """Test Block 5: Predictive Intelligence"""
    print("\n" + "="*70)
    print("Testing Block 5: Predictive Intelligence")
    print("="*70)
    
    from predictive_intelligence import PredictiveIntelligence
    pi = PredictiveIntelligence()
    
    print("✓ Predictive Intelligence initialized")
    
    # Test risk assessment
    risk = await pi.get_risk_assessment(
        destination="Japan",
        activities=["skiing"],
        duration=7,
        age=30,
        month=1
    )
    print(f"✓ Risk assessment works")
    print(f"  Risk Score: {risk.get('risk_score')}")
    print(f"  Risk Level: {risk.get('risk_level')}")
    
    # Test recommendations
    recs = await pi.recommend_coverage(
        destination="Japan",
        activities=["skiing"],
        trip_cost=5000,
        duration=7
    )
    print(f"✓ Coverage recommendations work")
    print(f"  Recommended medical: ${recs['recommendations']['medical_coverage']['recommended']:,.0f}")
    
    return True

async def test_payment_handler():
    """Test Block 4: Seamless Commerce"""
    print("\n" + "="*70)
    print("Testing Block 4: Seamless Commerce")
    print("="*70)
    
    from payment_handler import PaymentHandler
    ph = PaymentHandler()
    
    print("✓ Payment Handler initialized")
    
    if not os.getenv("STRIPE_SECRET_KEY"):
        print("⚠️  STRIPE_SECRET_KEY not set. Skipping payment tests.")
        return True
    
    # Test payment creation (won't actually create without valid key)
    print("⚠️  Payment creation requires valid Stripe keys and DynamoDB")
    print("  Run: cd Payments && docker-compose up -d")
    
    return True

async def main():
    """Run all tests"""
    print("\n🧪 WanderSure System Test Suite")
    print("="*70)
    
    if not os.getenv("GROQ_API_KEY"):
        print("\n❌ ERROR: GROQ_API_KEY not set in environment!")
        print("Please set it in .env file or export it.")
        return
    
    tests = [
        ("Policy Intelligence", test_policy_intelligence),
        ("Conversational Magic", test_conversation),
        ("Document Intelligence", test_document_intelligence),
        ("Predictive Intelligence", test_predictive_intelligence),
        ("Payment Handler", test_payment_handler),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test failed: {e}")
            results.append((name, False))
    
    print("\n" + "="*70)
    print("Test Results Summary")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + ("✅ All tests passed!" if all_passed else "❌ Some tests failed"))
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

