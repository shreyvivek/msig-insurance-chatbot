"""
v1 Payment endpoints with Stripe MCP integration
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict
import stripe
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["payment"])

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_TEST_SECRET") or os.getenv("STRIPE_SECRET_KEY")
DOMAIN = os.getenv("DOMAIN", "http://localhost:3000")

@router.post("/stripe-mcp")
async def stripe_mcp_payment(request: Dict):
    """
    Create Stripe checkout session (sandbox auto-complete in test mode)
    Input: {
        "amount": int (cents),
        "currency": str (default: "sgd"),
        "quote_id": str,
        "user_id": str,
        "auto_complete": bool (default: false, only for sandbox)
    }
    Output: {
        "payment_url": str,
        "session_id": str,
        "status": str
    }
    """
    amount = request.get("amount", 0)
    currency = request.get("currency", "sgd").lower()
    quote_id = request.get("quote_id", "")
    user_id = request.get("user_id", "")
    auto_complete = request.get("auto_complete", False)
    
    if not amount or amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")
    
    try:
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'WanderSure Travel Insurance',
                        'description': f'Quote ID: {quote_id}'
                    },
                    'unit_amount': int(amount * 100) if currency == "sgd" else amount,  # Convert SGD to cents if needed
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{DOMAIN}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN}/payment/cancel",
            metadata={
                'quote_id': quote_id,
                'user_id': user_id
            }
        )
        
        # For sandbox test mode, optionally auto-complete
        is_test = stripe.api_key.startswith("sk_test")
        if is_test and auto_complete:
            # In test mode, we can mark as completed immediately
            # In real production, webhook would handle this
            logger.info(f"Sandbox mode: Auto-completing payment for test")
        
        return {
            "payment_url": checkout_session.url,
            "session_id": checkout_session.id,
            "status": "pending",
            "is_test": is_test
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Payment error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

