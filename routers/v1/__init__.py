"""
v1 API routers
"""
from fastapi import APIRouter
from .user import router as user_router
from .itinerary import router as itinerary_router
from .policy import router as policy_router
from .chat import router as chat_router
from .payment import router as payment_router

router = APIRouter(prefix="/v1")

router.include_router(user_router)
router.include_router(itinerary_router)
router.include_router(policy_router)
router.include_router(chat_router)
router.include_router(payment_router)

