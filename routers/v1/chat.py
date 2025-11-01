"""
v1 Chat endpoints with history management
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from datetime import datetime
import uuid
from database import db
from models.user_profile import ChatSession, ChatMessage
from conversation_handler import ConversationHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

conversation = ConversationHandler()

@router.post("/new")
async def create_new_chat(request: Dict):
    """
    Create new chat session, archive old one
    Input: {
        "user_id": str,
        "old_session_id": str (optional),
        "language": str (default: "en")
    }
    Output: {
        "session_id": str,
        "success": bool
    }
    """
    user_id = request.get("user_id", "anonymous")
    old_session_id = request.get("old_session_id")
    language = request.get("language", "en")
    
    try:
        # Archive old session if provided
        if old_session_id and db.is_connected():
            chat_history = db.get_collection("chat_history")
            session = chat_history.find_one({"session_id": old_session_id})
            
            if session:
                # Generate summary (simplified - could use LLM)
                messages = session.get("messages", [])
                summary = f"Chat with {len(messages)} messages"
                
                chat_history.update_one(
                    {"session_id": old_session_id},
                    {
                        "$set": {
                            "archived_at": datetime.now(),
                            "summary": summary
                        }
                    }
                )
                logger.info(f"Archived session {old_session_id}")
        
        # Create new session
        new_session_id = str(uuid.uuid4())
        
        if db.is_connected():
            chat_history = db.get_collection("chat_history")
            chat_history.insert_one({
                "session_id": new_session_id,
                "user_id": user_id,
                "messages": [],
                "language": language,
                "created_at": datetime.now(),
                "archived_at": None
            })
        
        return {
            "session_id": new_session_id,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error creating new chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20):
    """
    List saved chat sessions for user
    """
    if not db.is_connected():
        return {"sessions": []}
    
    try:
        chat_history = db.get_collection("chat_history")
        sessions = list(
            chat_history.find(
                {"user_id": user_id, "archived_at": {"$ne": None}}
            )
            .sort("archived_at", -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for session in sessions:
            session["_id"] = str(session["_id"])
            if "messages" in session:
                session["message_count"] = len(session["messages"])
        
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def chat(request: Dict):
    """
    Enhanced chat endpoint with full context
    Input: {
        "question": str,
        "user_id": str,
        "session_id": str,
        "language": str (optional),
        "user_profile": Dict (optional),
        "itinerary": Dict (optional)
    }
    """
    question = request.get("question", "").strip()
    user_id = request.get("user_id", "anonymous")
    session_id = request.get("session_id")
    language = request.get("language", "en")
    
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    
    try:
        # Get user profile if available
        user_profile = {}
        if db.is_connected():
            users = db.get_collection("users")
            user = users.find_one({"user_id": user_id})
            if user:
                user_profile = {
                    "adventurous_score": user.get("adventurous_score", 0.0),
                    "policy_tier": user.get("policy_tier", "free"),
                    "likely_activities": user.get("likely_activities", [])
                }
        
        # Save user message to history
        user_message = {
            "role": "user",
            "content": question,
            "timestamp": datetime.now()
        }
        
        if session_id and db.is_connected():
            chat_history = db.get_collection("chat_history")
            chat_history.update_one(
                {"session_id": session_id},
                {"$push": {"messages": user_message}}
            )
        
        # Get response (reuse existing conversation handler but with enhanced context)
        context_data = {
            "user_profile": user_profile,
            "language": language,
            "itinerary": request.get("itinerary", {})
        }
        
        response_data = {
            "question": question,
            "user_id": user_id,
            "context_data": context_data
        }
        
        # Use existing ask endpoint logic
        from run_server import ask_question
        result = await ask_question(response_data)
        
        # Save assistant response to history
        assistant_message = {
            "role": "assistant",
            "content": result.get("response", ""),
            "timestamp": datetime.now()
        }
        
        if session_id and db.is_connected():
            chat_history = db.get_collection("chat_history")
            chat_history.update_one(
                {"session_id": session_id},
                {"$push": {"messages": assistant_message}}
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

