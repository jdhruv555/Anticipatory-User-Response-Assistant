"""REST API routes"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from models.database import get_db_session
from models.schemas import Customer, CallHistory

router = APIRouter()


class CallOutcome(BaseModel):
    """Call outcome model"""
    satisfaction: Optional[float] = None
    resolved: bool = False
    notes: Optional[str] = None


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer profile"""
    async with get_db_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {
            "id": customer.id,
            "customer_type": customer.customer_type,
            "total_calls": customer.total_calls,
            "satisfaction_avg": customer.satisfaction_avg,
            "resolution_rate": customer.resolution_rate,
            "preferred_persona": customer.preferred_persona
        }


@router.get("/calls/{call_id}/history")
async def get_call_history(call_id: str):
    """Get call history"""
    async with get_db_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(CallHistory).where(CallHistory.id == call_id)
        )
        call = result.scalar_one_or_none()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return {
            "id": call.id,
            "customer_id": call.customer_id,
            "persona_used": call.persona_used,
            "intent": call.intent,
            "satisfaction_score": call.satisfaction_score,
            "resolved": call.resolved,
            "outcome": call.outcome,
            "duration_seconds": call.duration_seconds,
            "timestamp": call.timestamp.isoformat() if call.timestamp else None
        }


@router.get("/customers/{customer_id}/calls")
async def get_customer_calls(customer_id: str, limit: int = 10):
    """Get customer's call history"""
    async with get_db_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(CallHistory)
            .where(CallHistory.customer_id == customer_id)
            .order_by(CallHistory.timestamp.desc())
            .limit(limit)
        )
        calls = result.scalars().all()
        
        return [
            {
                "id": call.id,
                "persona_used": call.persona_used,
                "intent": call.intent,
                "satisfaction_score": call.satisfaction_score,
                "resolved": call.resolved,
                "timestamp": call.timestamp.isoformat() if call.timestamp else None
            }
            for call in calls
        ]


@router.post("/calls/{call_id}/outcome")
async def record_call_outcome(call_id: str, outcome: CallOutcome):
    """Record call outcome (typically called via WebSocket, but available as REST endpoint)"""
    # This is mainly handled by the WebSocket endpoint
    # This REST endpoint is for manual updates or batch processing
    return {"status": "recorded", "call_id": call_id, "outcome": outcome.dict()}

