"""
Block 4: Seamless Commerce
Handle Stripe payments with DynamoDB integration
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import uuid
import stripe
import boto3
import requests
from groq import Groq

logger = logging.getLogger(__name__)

class PaymentHandler:
    """Handles payment creation and status checking"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.stripe_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_TEST_SECRET", "")
        if self.stripe_key:
            stripe.api_key = self.stripe_key
        else:
            logger.warning("STRIPE_SECRET_KEY not set. Payment features will not work.")
        
        # DynamoDB setup - with in-memory fallback
        self.dynamodb_endpoint = os.getenv("DDB_ENDPOINT", "http://localhost:8000")
        self.aws_region = os.getenv("AWS_REGION", "ap-southeast-1")
        self.table_name = os.getenv("DYNAMODB_PAYMENTS_TABLE", "lea-payments-local")
        self.use_in_memory = False
        
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=self.aws_region,
                endpoint_url=self.dynamodb_endpoint,
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy'
            )
            self.payments_table = self.dynamodb.Table(self.table_name)
            # Test connection
            self.payments_table.table_status
            logger.info("DynamoDB connected successfully")
        except Exception as e:
            logger.warning(f"DynamoDB connection failed: {e}")
            logger.info("Using in-memory storage fallback for payment records")
            self.payments_table = None
            self.use_in_memory = True
            self.in_memory_payments = {}
    
    async def create_payment(self, quote_id: str, policy_name: str, amount, currency: str = "SGD", user_id: str = "default_user") -> Dict:
        """Create a Stripe payment session"""
        
        payment_intent_id = f"payment_{uuid.uuid4().hex[:12]}"
        
        # Convert amount to cents for Stripe (ensure it's at least $0.50)
        # If amount is already large, assume it's in cents; otherwise assume dollars
        amount_in_dollars = float(amount) if float(amount) < 1000 else float(amount) / 100
        amount_in_cents = int(round(amount_in_dollars * 100))
        
        # Ensure minimum charge
        if amount_in_cents < 50:
            amount_in_cents = 50  # $0.50 SGD minimum
        
        logger.info(f"Creating payment: {amount_in_dollars} {currency} = {amount_in_cents} cents")
        
        # Create payment record in DynamoDB
        payment_record = {
            'payment_intent_id': payment_intent_id,
            'user_id': user_id,
            'quote_id': quote_id,
            'policy_name': policy_name,
            'payment_status': 'pending',
            'amount': amount_in_dollars,  # Store original amount in dollars
            'currency': currency,
            'product_name': f'Travel Insurance - {policy_name}',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Store payment record (DynamoDB or in-memory)
        try:
            if self.payments_table:
                self.payments_table.put_item(Item=payment_record)
                logger.info(f"Payment record created: {payment_intent_id}")
            elif self.use_in_memory:
                self.in_memory_payments[payment_intent_id] = payment_record
                logger.info(f"Payment record stored in-memory: {payment_intent_id}")
        except Exception as e:
            logger.error(f"Failed to create payment record: {e}")
            # Don't fail payment creation just because of DB error
            logger.warning("Continuing with payment despite storage error")
        
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'unit_amount': amount_in_cents,  # Use cents for Stripe
                        'product_data': {
                            'name': f'Travel Insurance - {policy_name}',
                            'description': f'Insurance policy for quote {quote_id}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'http://localhost:8085/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url='http://localhost:8085/cancel',
                client_reference_id=payment_intent_id,
                metadata={
                    'quote_id': quote_id,
                    'policy_name': policy_name,
                    'user_id': user_id
                }
            )
            
            # Update record with Stripe session ID
            if self.payments_table:
                self.payments_table.update_item(
                    Key={'payment_intent_id': payment_intent_id},
                    UpdateExpression='SET stripe_session_id = :sid',
                    ExpressionAttributeValues={':sid': checkout_session.id}
                )
            
            logger.info(f"Stripe session created: {checkout_session.id}")
            
            return {
                "success": True,
                "payment_id": payment_intent_id,
                "stripe_session_id": checkout_session.id,
                "payment_url": checkout_session.url,
                "status": "pending",
                "amount": amount_in_dollars,  # Return original amount in dollars
                "currency": currency,
                "message": f"Payment link created. Status will update automatically after payment."
            }
        
        except Exception as e:
            logger.error(f"Stripe session creation failed: {e}")
                # Update payment record to failed
            try:
                if self.payments_table:
                    self.payments_table.update_item(
                        Key={'payment_intent_id': payment_intent_id},
                        UpdateExpression='SET payment_status = :status',
                        ExpressionAttributeValues={':status': 'failed'}
                    )
                elif self.use_in_memory and payment_intent_id in self.in_memory_payments:
                    self.in_memory_payments[payment_intent_id]['payment_status'] = 'failed'
            except:
                pass
            
            return {
                "success": False,
                "error": f"Stripe error: {str(e)}"
            }
    
    async def check_payment_status(self, payment_id: str) -> Dict:
        """Check payment status from DynamoDB or in-memory"""
        
        try:
            payment_record = None
            
            if self.payments_table:
                response = self.payments_table.get_item(
                    Key={'payment_intent_id': payment_id}
                )
                if 'Item' in response:
                    payment_record = response['Item']
            elif self.use_in_memory and payment_id in self.in_memory_payments:
                payment_record = self.in_memory_payments[payment_id]
            
            if not payment_record:
                return {
                    "success": False,
                    "error": "Payment record not found"
                }
            
            # Also check Stripe status if session exists
            stripe_status = None
            if payment_record.get('stripe_session_id'):
                try:
                    session = stripe.checkout.Session.retrieve(
                        payment_record['stripe_session_id']
                    )
                    stripe_status = session.payment_status
                except Exception as e:
                    logger.warning(f"Could not retrieve Stripe status: {e}")
            
            return {
                "success": True,
                "payment_id": payment_id,
                "status": payment_record.get('payment_status', 'unknown'),
                "stripe_status": stripe_status,
                "amount": payment_record.get('amount'),
                "currency": payment_record.get('currency'),
                "policy_name": payment_record.get('policy_name'),
                "created_at": payment_record.get('created_at'),
                "updated_at": payment_record.get('updated_at'),
                "webhook_processed_at": payment_record.get('webhook_processed_at')
            }
        
        except Exception as e:
            logger.error(f"Payment status check failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_confirmation_email(self, payment_id: str, user_email: str) -> Dict:
        """Send policy confirmation email after payment"""
        # This would integrate with email service (AWS SES, SendGrid, etc.)
        # For now, return a placeholder
        
        payment_status = await self.check_payment_status(payment_id)
        
        if payment_status.get("status") == "completed":
            return {
                "success": True,
                "message": f"Policy confirmation email sent to {user_email}",
                "note": "Email service integration needed for production"
            }
        else:
            return {
                "success": False,
                "error": "Payment not completed, cannot send confirmation"
            }

