"""
Partner Integrations - Mock integrations with booking platforms and travel services
Simulates realistic data retrieval from partner systems
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class PartnerIntegrations:
    """Mock partner integrations for realistic travel data retrieval"""
    
    def __init__(self):
        # Mock booking platform data
        self.mock_bookings = {
            # Sample booking 1
            "booking_ref_12345": {
                "booking_reference": "ABC12345",
                "platform": "Expedia",
                "travelers": [
                    {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone": "+65 9123 4567",
                        "age": 39,
                        "dateOfBirth": "1985-03-15",
                        "passport": "K12345678"
                    }
                ],
                "flight": {
                    "airline": "Singapore Airlines",
                    "flight_number": "SQ318",
                    "departure_airport": "SIN",
                    "arrival_airport": "NRT",
                    "departure_date": "2024-12-20",
                    "return_date": "2024-12-27",
                    "ticket_price": 1250.00
                },
                "hotel": {
                    "name": "Tokyo Grand Hotel",
                    "check_in": "2024-12-20",
                    "check_out": "2024-12-27",
                    "location": "Tokyo, Japan"
                },
                "destination": "Japan",
                "activities": ["sightseeing", "shopping", "dining"]
            },
            # Sample booking 2
            "booking_ref_67890": {
                "booking_reference": "XYZ67890",
                "platform": "Booking.com",
                "travelers": [
                    {
                        "name": "Sarah Chen",
                        "email": "sarah.chen@example.com",
                        "phone": "+65 8765 4321",
                        "age": 34,
                        "dateOfBirth": "1990-07-22",
                        "passport": "K98765432"
                    },
                    {
                        "name": "David Chen",
                        "email": "david.chen@example.com",
                        "age": 36,
                        "dateOfBirth": "1988-05-10"
                    }
                ],
                "flight": {
                    "airline": "Cathay Pacific",
                    "flight_number": "CX712",
                    "departure_airport": "SIN",
                    "arrival_airport": "BKK",
                    "departure_date": "2024-11-15",
                    "return_date": "2024-11-22",
                    "ticket_price": 680.00
                },
                "hotel": {
                    "name": "Bangkok Resort",
                    "check_in": "2024-11-15",
                    "check_out": "2024-11-22",
                    "location": "Bangkok, Thailand"
                },
                "destination": "Thailand",
                "activities": ["beach", "spa", "diving"]
            }
        }
        
        # Mock email/calendar integration
        self.mock_email_bookings = {
            "john.doe@example.com": [
                {
                    "source": "email_confirmation",
                    "subject": "Your Singapore Airlines Booking Confirmation",
                    "extracted": {
                        "airline": "Singapore Airlines",
                        "flight_number": "SQ318",
                        "destination": "Tokyo, Japan",
                        "departure_date": "2024-12-20",
                        "return_date": "2024-12-27",
                        "travelers": ["John Doe"]
                    }
                }
            ]
        }
    
    async def get_booking_by_reference(self, booking_ref: str, email: str = None) -> Optional[Dict]:
        """Retrieve booking from partner platform by reference"""
        # Simulate API call delay
        import asyncio
        await asyncio.sleep(0.1)
        
        # Check mock bookings
        for key, booking in self.mock_bookings.items():
            if booking["booking_reference"] == booking_ref.upper():
                return booking
        
        # If email provided, check if user matches
        if email:
            for booking in self.mock_bookings.values():
                travelers = booking.get("travelers", [])
                if any(t.get("email", "").lower() == email.lower() for t in travelers):
                    return booking
        
        return None
    
    async def get_bookings_by_email(self, email: str) -> List[Dict]:
        """Retrieve all bookings for an email address"""
        import asyncio
        await asyncio.sleep(0.1)
        
        bookings = []
        email_lower = email.lower()
        
        for booking in self.mock_bookings.values():
            travelers = booking.get("travelers", [])
            if any(t.get("email", "").lower() == email_lower for t in travelers):
                bookings.append(booking)
        
        # Also check email integrations
        email_bookings = self.mock_email_bookings.get(email_lower, [])
        for email_booking in email_bookings:
            bookings.append(email_booking.get("extracted", {}))
        
        return bookings
    
    async def get_upcoming_trips(self, email: str, days_ahead: int = 90) -> List[Dict]:
        """Get upcoming trips within specified days"""
        import asyncio
        all_bookings = await self.get_bookings_by_email(email)
        upcoming = []
        today = datetime.now().date()
        
        for booking in all_bookings:
            dep_date_str = booking.get("flight", {}).get("departure_date") or \
                          booking.get("departure_date") or \
                          booking.get("extracted", {}).get("departure_date")
            
            if dep_date_str:
                try:
                    dep_date = datetime.strptime(dep_date_str, "%Y-%m-%d").date()
                    if today <= dep_date <= (today + timedelta(days=days_ahead)):
                        upcoming.append(booking)
                except:
                    pass
        
        return sorted(upcoming, key=lambda x: x.get("flight", {}).get("departure_date", ""))
    
    async def get_travel_details_from_calendar(self, email: str) -> Optional[Dict]:
        """Extract travel details from calendar events (mock)"""
        import asyncio
        await asyncio.sleep(0.1)
        
        # Mock calendar integration - simulate finding travel events
        calendar_events = self.mock_email_bookings.get(email.lower(), [])
        if calendar_events:
            # Return most recent/future event
            for event in reversed(calendar_events):
                extracted = event.get("extracted", {})
                if extracted:
                    return extracted
        
        return None
    
    async def sync_user_data(self, email: str) -> Dict:
        """Sync user data from multiple partner sources"""
        results = {
            "bookings": await self.get_bookings_by_email(email),
            "upcoming_trips": await self.get_upcoming_trips(email),
            "calendar_events": await self.get_travel_details_from_calendar(email)
        }
        
        return results

