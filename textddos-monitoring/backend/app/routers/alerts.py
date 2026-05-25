from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime

from app.schemas.flow import AlertCreate, AlertResponse, AlertUpdate
from app.core.database import get_alerts_collection
from app.services.websocket_manager import websocket_manager

router = APIRouter()

@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    background_tasks: BackgroundTasks,
    alerts_collection: AsyncIOMotorCollection = Depends(get_alerts_collection)
):
    """Create a new alert"""
    alert_data = alert.dict()
    alert_data.update({
        "timestamp": datetime.utcnow(),
        "status": "new",
        "actions_taken": []
    })

    result = await alerts_collection.insert_one(alert_data)
    alert_data["_id"] = result.inserted_id

    # Broadcast alert to WebSocket clients
    await websocket_manager.broadcast_alert(alert_data)

    # Add background task for alert processing
    background_tasks.add_task(process_alert_actions, alert_data)

    return AlertResponse(**alert_data)

@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    alerts_collection: AsyncIOMotorCollection = Depends(get_alerts_collection)
):
    """Get alerts with filtering"""
    query = {}

    if status:
        query["status"] = status
    if severity:
        query["severity"] = severity

    alerts = await alerts_collection.find(query)\
        .sort("timestamp", -1)\
        .skip(skip)\
        .limit(limit)\
        .to_list(length=None)

    return [AlertResponse(**alert) for alert in alerts]

@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    alerts_collection: AsyncIOMotorCollection = Depends(get_alerts_collection)
):
    """Get a specific alert"""
    from bson import ObjectId
    alert = await alerts_collection.find_one({"_id": ObjectId(alert_id)})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertResponse(**alert)

@router.put("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    alerts_collection: AsyncIOMotorCollection = Depends(get_alerts_collection)
):
    """Update an alert"""
    from bson import ObjectId
    update_data = {k: v for k, v in alert_update.dict().items() if v is not None}

    result = await alerts_collection.update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")

    updated_alert = await alerts_collection.find_one({"_id": ObjectId(alert_id)})
    return AlertResponse(**updated_alert)

@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    alerts_collection: AsyncIOMotorCollection = Depends(get_alerts_collection)
):
    """Delete an alert"""
    from bson import ObjectId
    result = await alerts_collection.delete_one({"_id": ObjectId(alert_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"message": "Alert deleted successfully"}

@router.post("/alerts/{alert_id}/block-ip")
async def block_ip(
    alert_id: str,
    alerts_collection: AsyncIOMotorCollection = Depends(get_alerts_collection)
):
    """Block IP address associated with alert"""
    from bson import ObjectId

    alert = await alerts_collection.find_one({"_id": ObjectId(alert_id)})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Add action to alert
    await alerts_collection.update_one(
        {"_id": ObjectId(alert_id)},
        {
            "$push": {"actions_taken": f"Blocked IP {alert['src_ip']}"},
            "$set": {"status": "acknowledged"}
        }
    )

    # TODO: Implement actual IP blocking logic
    # This could integrate with firewall rules, iptables, etc.

    return {"message": f"IP {alert['src_ip']} blocked successfully"}

@router.post("/alerts/{alert_id}/add-to-blacklist")
async def add_to_blacklist(
    alert_id: str,
    alerts_collection: AsyncIOMotorCollection = Depends(get_alerts_collection)
):
    """Add IP to blacklist"""
    from bson import ObjectId

    alert = await alerts_collection.find_one({"_id": ObjectId(alert_id)})
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Add action to alert
    await alerts_collection.update_one(
        {"_id": ObjectId(alert_id)},
        {
            "$push": {"actions_taken": f"Added IP {alert['src_ip']} to blacklist"},
            "$set": {"status": "acknowledged"}
        }
    )

    # TODO: Implement blacklist logic
    # This could update a blacklist database/collection

    return {"message": f"IP {alert['src_ip']} added to blacklist"}

async def process_alert_actions(alert_data: dict):
    """Process alert actions in background"""
    # TODO: Implement alert action processing
    # This could send notifications, update firewall rules, etc.
    pass
