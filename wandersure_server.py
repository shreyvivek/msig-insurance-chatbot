#!/usr/bin/env python3
"""
WanderSure - Smart Travel Insurance Companion
MCP Server Implementation

Main MCP server that orchestrates all functionality:
- Policy Intelligence (Block 1)
- Conversational Magic (Block 2)
- Document Intelligence (Block 3)
- Seamless Commerce (Block 4)
- Predictive Intelligence (Block 5)
"""

import os
import json
import asyncio
import logging
from typing import Any, Optional, Dict, List
from pathlib import Path
import uuid
from datetime import datetime
import base64

try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource, Tool, TextContent, ImageContent, EmbeddedResource,
        LoggingLevel
    )
    import mcp.types as types
except ImportError:
    # Fallback for older MCP versions
    from mcp import types
    stdio_server = None

# Import our modules
from policy_intelligence import PolicyIntelligence
from document_intelligence import DocumentIntelligence
from predictive_intelligence import PredictiveIntelligence
from payment_handler import PaymentHandler
from conversation_handler import ConversationHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("wandersure")

# Initialize modules
policy_intel = PolicyIntelligence()
doc_intel = DocumentIntelligence()
predictive_intel = PredictiveIntelligence()
payment_handler = PaymentHandler()
conversation = ConversationHandler()

# Create MCP server
server = Server("wandersure")

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources (policy documents, normalized data, etc.)"""
    resources = [
        Resource(
            uri="wandersure://policies/normalized",
            name="Normalized Policy Data",
            description="Structured insurance policy data normalized to taxonomy",
            mimeType="application/json"
        ),
        Resource(
            uri="wandersure://claims/insights",
            name="Claims Intelligence",
            description="Predictive insights from historical claims data",
            mimeType="application/json"
        ),
        Resource(
            uri="wandersure://conversation/memory",
            name="Conversation Memory",
            description="User preferences and conversation context",
            mimeType="application/json"
        )
    ]
    
    # Add policy resources
    for policy in policy_intel.get_policy_list():
        resources.append(
            Resource(
                uri=f"wandersure://policy/{policy['id']}",
                name=policy['name'],
                description=f"Original policy document: {policy['name']}",
                mimeType="application/pdf"
            )
        )
    
    return resources

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI"""
    if uri.startswith("wandersure://policies/normalized"):
        data = policy_intel.get_normalized_data()
        return json.dumps(data, indent=2)
    
    elif uri.startswith("wandersure://claims/insights"):
        insights = predictive_intel.get_insights_summary()
        return json.dumps(insights, indent=2)
    
    elif uri.startswith("wandersure://conversation/memory"):
        memory = conversation.get_memory()
        return json.dumps(memory, indent=2)
    
    elif uri.startswith("wandersure://policy/"):
        policy_id = uri.split("/")[-1]
        policy_text = policy_intel.get_policy_text(policy_id)
        return policy_text or "Policy not found"
    
    return "Resource not found"

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools"""
    return [
        # Block 1: Policy Intelligence
        Tool(
            name="compare_policies",
            description="Compare insurance policies side-by-side on specific criteria. Can compare medical coverage, trip cancellation, baggage protection, age eligibility, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "criteria": {
                        "type": "string",
                        "description": "What to compare (e.g., 'medical coverage', 'trip cancellation', 'age eligibility', 'baggage protection')"
                    },
                    "policies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of policy names to compare (e.g., ['TravelEasy', 'Scootsurance'])"
                    }
                },
                "required": ["criteria"]
            }
        ),
        Tool(
            name="explain_coverage",
            description="Explain what's covered under a specific benefit or scenario. Returns detailed explanation with exact policy citations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "What to explain (e.g., 'trip cancellation', 'medical expenses', 'baggage loss', 'skiing accident')"
                    },
                    "policy": {
                        "type": "string",
                        "description": "Specific policy name (optional, if not provided explains for all policies)"
                    },
                    "scenario": {
                        "type": "string",
                        "description": "Specific scenario to analyze (e.g., 'if my flight is cancelled due to weather')"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="check_eligibility",
            description="Check if user is eligible for a policy based on age, health conditions, trip details, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "policy": {
                        "type": "string",
                        "description": "Policy name to check"
                    },
                    "age": {
                        "type": "integer",
                        "description": "User age"
                    },
                    "has_pre_existing": {
                        "type": "boolean",
                        "description": "Has pre-existing medical conditions"
                    },
                    "trip_duration": {
                        "type": "integer",
                        "description": "Trip duration in days"
                    }
                },
                "required": ["policy"]
            }
        ),
        
        # Block 2: Conversational Magic
        Tool(
            name="ask_question",
            description="Ask any question about travel insurance policies. The AI will understand context, provide citations, and maintain conversation flow.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "User's question about insurance"
                    },
                    "language": {
                        "type": "string",
                        "description": "Preferred language (auto-detected if not specified)"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context (e.g., trip destination, dates, activities)"
                    }
                },
                "required": ["question"]
            }
        ),
        
        # Block 3: Document Intelligence
        Tool(
            name="extract_trip_info",
            description="Extract trip information from uploaded documents (flight bookings, hotel reservations, itineraries). Returns structured trip data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_data": {
                        "type": "string",
                        "description": "Base64 encoded document or file path"
                    },
                    "document_type": {
                        "type": "string",
                        "enum": ["pdf", "image", "email", "text"],
                        "description": "Type of document"
                    }
                },
                "required": ["document_data", "document_type"]
            }
        ),
        Tool(
            name="generate_quote",
            description="Generate personalized insurance quote based on trip details and user preferences.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Trip destination"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Trip start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Trip end date (YYYY-MM-DD)"
                    },
                    "travelers": {
                        "type": "integer",
                        "description": "Number of travelers"
                    },
                    "ages": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Ages of travelers"
                    },
                    "activities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Planned activities (e.g., ['skiing', 'hiking', 'scuba diving'])"
                    },
                    "trip_cost": {
                        "type": "number",
                        "description": "Total trip cost"
                    }
                },
                "required": ["destination", "start_date", "end_date"]
            }
        ),
        
        # Block 4: Seamless Commerce
        Tool(
            name="create_payment",
            description="Create a Stripe payment session for purchasing insurance. Returns payment link.",
            inputSchema={
                "type": "object",
                "properties": {
                    "quote_id": {
                        "type": "string",
                        "description": "Quote identifier"
                    },
                    "policy_name": {
                        "type": "string",
                        "description": "Policy name to purchase"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount in cents"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (default: SGD)"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    }
                },
                "required": ["quote_id", "policy_name", "amount"]
            }
        ),
        Tool(
            name="check_payment_status",
            description="Check the status of a payment (pending, completed, failed, expired).",
            inputSchema={
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "string",
                        "description": "Payment intent ID"
                    }
                },
                "required": ["payment_id"]
            }
        ),
        
        # Block 5: Predictive Intelligence
        Tool(
            name="get_risk_assessment",
            description="Get personalized risk assessment and recommendations based on destination, activities, and historical claims data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Trip destination"
                    },
                    "activities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Planned activities"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Trip duration in days"
                    },
                    "age": {
                        "type": "integer",
                        "description": "Traveler age"
                    },
                    "month": {
                        "type": "integer",
                        "description": "Travel month (1-12)"
                    }
                },
                "required": ["destination"]
            }
        ),
        Tool(
            name="recommend_coverage",
            description="Get personalized coverage recommendations based on trip details and claims data insights.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Trip destination"
                    },
                    "activities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Planned activities"
                    },
                    "trip_cost": {
                        "type": "number",
                        "description": "Total trip cost"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Trip duration"
                    }
                },
                "required": ["destination"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        logger.info(f"Tool called: {name} with args: {arguments}")
        
        if name == "compare_policies":
            result = await policy_intel.compare_policies(
                criteria=arguments.get("criteria"),
                policies=arguments.get("policies", [])
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "explain_coverage":
            result = await policy_intel.explain_coverage(
                topic=arguments.get("topic"),
                policy=arguments.get("policy"),
                scenario=arguments.get("scenario")
            )
            return [types.TextContent(type="text", text=result)]
        
        elif name == "check_eligibility":
            result = await policy_intel.check_eligibility(
                policy=arguments.get("policy"),
                age=arguments.get("age"),
                has_pre_existing=arguments.get("has_pre_existing"),
                trip_duration=arguments.get("trip_duration")
            )
            return [types.TextContent(type="text", text=result)]
        
        elif name == "ask_question":
            result = await conversation.handle_question(
                question=arguments.get("question"),
                language=arguments.get("language"),
                context=arguments.get("context")
            )
            return [types.TextContent(type="text", text=result)]
        
        elif name == "extract_trip_info":
            result = await doc_intel.extract_trip_info(
                document_data=arguments.get("document_data"),
                document_type=arguments.get("document_type")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "generate_quote":
            result = await doc_intel.generate_quote(
                destination=arguments.get("destination"),
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date"),
                travelers=arguments.get("travelers", 1),
                ages=arguments.get("ages", []),
                activities=arguments.get("activities", []),
                trip_cost=arguments.get("trip_cost")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "create_payment":
            result = await payment_handler.create_payment(
                quote_id=arguments.get("quote_id"),
                policy_name=arguments.get("policy_name"),
                amount=int(arguments.get("amount")),
                currency=arguments.get("currency", "SGD"),
                user_id=arguments.get("user_id", "default_user")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "check_payment_status":
            result = await payment_handler.check_payment_status(
                payment_id=arguments.get("payment_id")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_risk_assessment":
            result = await predictive_intel.get_risk_assessment(
                destination=arguments.get("destination"),
                activities=arguments.get("activities", []),
                duration=arguments.get("duration"),
                age=arguments.get("age"),
                month=arguments.get("month")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "recommend_coverage":
            result = await predictive_intel.recommend_coverage(
                destination=arguments.get("destination"),
                activities=arguments.get("activities", []),
                trip_cost=arguments.get("trip_cost"),
                duration=arguments.get("duration")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Run the MCP server"""
    if stdio_server is None:
        logger.error("MCP stdio_server not available. Use run_server.py instead.")
        return
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="wandersure",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except Exception as e:
        logger.error(f"MCP server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

