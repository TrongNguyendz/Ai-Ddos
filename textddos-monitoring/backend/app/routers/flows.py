
from sympy import limit

from fastapi import APIRouter, HTTPException, Depends, Query,Request,Response
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
import asyncio
from app.schemas.flow import (
    FlowCreate, FlowResponse, FlowUpdate, FlowStats,
    DashboardStats, ChartData, TopIP
)
from app.core.database import get_flows_collection, get_stats_collection
from app.services.inference import predict_flow
from app.services.websocket_manager import websocket_manager
from app.core.config import settings
from datetime import datetime, timezone, timedelta
from loguru import logger
from app.core.rate_limiter import limiter
router = APIRouter()
VN_TZ = timezone(timedelta(hours=7))


@router.post("/flows", response_model=FlowResponse)
async def create_flow(
    flow: FlowCreate,
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection)
):
    """Create a new flow with AI prediction"""
    prediction = await predict_flow(flow.dict())

    flow_data = flow.dict()
    logger.info("thời gian ghi nhận là: {}", datetime.now(VN_TZ))
    
    flow_data.update({
        "timestamp": datetime.now(VN_TZ),
        "label": prediction["label"],
        "confidence": prediction["confidence"]
    })

    result = await flows_collection.insert_one(flow_data)
    flow_data["_id"] = result.inserted_id

    await websocket_manager.broadcast_flow(flow_data)

    flow_data["id"] = str(flow_data["_id"])
    del flow_data["_id"]

    return FlowResponse(**flow_data)


@router.get("/flows", response_model=List[FlowResponse])
@limiter.limit("30/minute")                    # ← Sửa đơn giản như này
async def get_flows(
    request: Request,                          # Bắt buộc
    response: Response,                        # Bắt buộc để inject headers
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    switch: Optional[str] = None,
    protocol: Optional[str] = None,
    label: Optional[int] = None,
    src_ip: Optional[str] = None,
    dst_ip: Optional[str] = None,
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection)
):
    """Get flows with filtering and pagination - Sort theo thời gian mới nhất"""
    query = {}

    if switch:
        query["switch"] = switch
    if protocol:
        query["protocol"] = protocol
    if label is not None:
        query["label"] = label
    if src_ip:
        query["src_ip"] = {"$regex": src_ip, "$options": "i"}
    if dst_ip:
        query["dst_ip"] = {"$regex": dst_ip, "$options": "i"}

    cursor = flows_collection.find(query).sort("timestamp", -1)
    flows = await cursor.skip(skip).limit(limit).to_list(length=None)

    # Convert timezone
    for flow in flows:
        if isinstance(flow.get("timestamp"), datetime):
            flow["timestamp"] = flow["timestamp"].replace(tzinfo=timezone.utc).astimezone(VN_TZ)

    return [
        FlowResponse(**{**flow, "id": str(flow["_id"])}) 
        for flow in flows
    ]

@router.get("/flows/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: str,
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection)
):
    """Get a specific flow by ID"""
    from bson import ObjectId
    flow = await flows_collection.find_one({"_id": ObjectId(flow_id)})
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    flow["id"] = str(flow["_id"])
    return FlowResponse(**flow)

@router.put("/flows/{flow_id}", response_model=FlowResponse)
async def update_flow(
    flow_id: str,
    flow_update: FlowUpdate,
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection)
):
    """Update a flow"""
    from bson import ObjectId
    update_data = {k: v for k, v in flow_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(VN_TZ)

    result = await flows_collection.update_one(
        {"_id": ObjectId(flow_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Flow not found")

    updated_flow = await flows_collection.find_one({"_id": ObjectId(flow_id)})
    updated_flow["id"] = str(updated_flow["_id"])
    return FlowResponse(**updated_flow)

@router.delete("/flows/{flow_id}")
async def delete_flow(
    flow_id: str,
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection)
):
    """Delete a flow"""
    from bson import ObjectId
    result = await flows_collection.delete_one({"_id": ObjectId(flow_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Flow not found")

    return {"message": "Flow deleted successfully"}

@router.get("/flows/stats/realtime", response_model=FlowStats)
async def get_realtime_stats(
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection)
):
    """Get real-time flow statistics"""
    # Get flows from last 5 minutes
    five_minutes_ago = datetime.now(VN_TZ) - timedelta(minutes=5)
    recent_flows = await flows_collection.find(
        {"timestamp": {"$gte": five_minutes_ago}}
    ).to_list(length=limit)

    total_flows = len(recent_flows)
    attack_flows = len([f for f in recent_flows if f.get("label") == 1])
    normal_flows = total_flows - attack_flows
    attack_percentage = (attack_flows / total_flows * 100) if total_flows > 0 else 0

    # Calculate top IPs
    from collections import Counter
    attacking_ips = Counter(f["src_ip"] for f in recent_flows if f.get("label") == 1)
    targeted_ips = Counter(f["dst_ip"] for f in recent_flows)

    top_attacking = [{"ip": ip, "count": count} for ip, count in attacking_ips.most_common(5)]
    top_targeted = [{"ip": ip, "count": count} for ip, count in targeted_ips.most_common(5)]

    return FlowStats(
        total_flows=total_flows,
        attack_flows=attack_flows,
        normal_flows=normal_flows,
        attack_percentage=round(attack_percentage, 2),
        top_attacking_ips=top_attacking,
        top_targeted_ips=top_targeted
    )
