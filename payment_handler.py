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
        self.stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
        if self.stripe_key:
            stripe.api_key = self.stripe_key
        else:
            logger.warning("STRIPE_SECRET_KEY not set. Payment features will not work.")
        
        # DynamoDB setup
        self.dynamodb_endpoint = os.getenv("DDB_ENDPOINT", "http://localhost:8000")
        self.aws_region = os.getenv("AWS_REGION", "ap-southeast-1")
        self.table_name = os.getenv("DYNAMODB_PAYMENTS_TABLE", "lea-payments-local")
        
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=self.aws_region,
                endpoint_url=self.dynamodb_endpoint,
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy'
            )
            self.payments_table = self.dynamodb.Table(self.table_name)
            logger.info("DynamoDB connected successfully")
        except Exception as e:
            logger.error(f"DynamoDB connection failed: {e}")
            self.payments_table = None
    
    async def create_payment(self, quote_id: str, policy_name: str, amount: int,
                            currency: str = "SGD", user_id: str = "default_user") -> Dict:
        """Create a Stripe payment session"""
        
        payment_intent_id = f"payment_{uuid.uuid4().hex[:12]}"
        
        # Create payment record in DynamoDB
        payment_record = {
            'payment_intent_id': payment_intent_id,
            'user_id': user_id,
            'quote_id': quote_id,
            'policy_name': policy_name,
            'payment_status': 'pending',
            'amount': amount,
            'currency': currency,
            'product_name': f'Travel Insurance - {policy_name}',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        try:
            if self.payments_table:
                self.payments_table.put_item(Item=payment_record)
                logger.info(f"Payment record created: {payment_intent_id}")
        except Exception as e:
            logger.error(f"Failed to create payment record: {e}")
            return {
                "success": False,
                "error": f"DynamoDB error: {str(e)}"
            }
        
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'unit_amount': amount,
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
                "amount": amount,
                "currency": currency,
                "message": f"Payment link created. Status will update automatically after payment."
            }
        
        except Exception as e:
            logger.error(f"Stripe session creation failed: {e}")
            # Update payment record to failed
            if self.payments_table:
                try:
                    self.payments_table.update_item(
                        Key={'payment_intent_id': payment_intent_id},
                        UpdateExpression='SET payment_status = :status',
                        ExpressionAttributeValues={':status': 'failed'}
                    )
                except:
                    pass
            
            return {
                "success": False,
                "error": f"Stripe error: {str(e)}"
            }
    
    async def check_payment_status(self, payment_id: str) -> Dict:
        """Check payment status from DynamoDB"""
        
        try:
            if not self.payments_table:
                return {
                    "success": False,
                    "error": "DynamoDB not available"
                }
            
            response = self.payments_table.get_item(
                Key={'payment_intent_id': payment_id}
            )
            
            if 'Item' not in response:
                return {
                    "success": False,
                    "error": "Payment record not found"
                }
            
            payment_record = response['Item']
            
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

