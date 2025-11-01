"""
v1 Policy comparison endpoints
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict
from services.policy_comparator import PolicyComparator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/policy", tags=["policy"])

policy_comparator = PolicyComparator()

@router.post("/compare-quant")
async def compare_policies_quantitative(request: Dict):
    """
    Quantitative policy comparison for scenario
    Input: {
        "policy_ids": ["TravelEasy", "Scootsurance"],
        "scenario": {
            "destination": str,
            "activities": List[str],
            "age": int (optional),
            "duration": int (optional)
        }
    }
    Output: {
        "benefit_comparison_table": List[Dict],
        "composite_scores": Dict,
        "best_policy": str,
        "justification": str,
        "citations": List[Dict]
    }
    """
    policy_ids = request.get("policy_ids", [])
    scenario = request.get("scenario", {})
    
    if len(policy_ids) != 2:
        raise HTTPException(status_code=400, detail="Exactly 2 policy_ids required")
    
    if not scenario.get("destination"):
        raise HTTPException(status_code=400, detail="scenario.destination is required")
    
    try:
        result = await policy_comparator.compare(
            policy_ids[0],
            policy_ids[1],
            scenario
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error comparing policies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

