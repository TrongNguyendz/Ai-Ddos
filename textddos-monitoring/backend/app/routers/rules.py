from fastapi import APIRouter, HTTPException, Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime
from bson import ObjectId

from app.schemas.rule import RuleCreate, RuleResponse, RuleUpdate
from app.core.database import get_rules_collection
from app.services.rule_engine_cloud_flare import evaluate_rules

router = APIRouter()

# ==================== HELPER FUNCTION ====================
def convert_mongo_to_response(rule_dict: dict):
    """Convert MongoDB document to RuleResponse compatible dict"""
    if not rule_dict:
        return None
    if "_id" in rule_dict:
        rule_dict["id"] = str(rule_dict.pop("_id"))
    return RuleResponse(**rule_dict)


# ==================== CREATE RULE (đã sửa trước) ====================
@router.post("/rules", response_model=RuleResponse)
async def create_rule(
    rule: RuleCreate,
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Create a new rule"""
    rule_data = rule.dict()
    rule_data.update({
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "triggered_count": 0,
        "last_triggered": None
    })

    result = await rules_collection.insert_one(rule_data)
    created_rule = await rules_collection.find_one({"_id": result.inserted_id})
    
    return convert_mongo_to_response(created_rule)


# ==================== CÁC ENDPOINT ĐÃ SỬA ====================
@router.get("/rules", response_model=List[RuleResponse])
async def get_rules(
    skip: int = 0,
    limit: int = 50,
    enabled: bool = None,
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Get rules with filtering"""
    query = {}
    if enabled is not None:
        query["enabled"] = enabled

    rules = await rules_collection.find(query)\
        .sort("created_at", -1)\
        .skip(skip)\
        .limit(limit)\
        .to_list(length=None)

    return [convert_mongo_to_response(rule) for rule in rules]


@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str,
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Get a specific rule"""
    try:
        rule = await rules_collection.find_one({"_id": ObjectId(rule_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return convert_mongo_to_response(rule)


@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: str,
    rule_update: RuleUpdate,
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Update a rule"""
    try:
        obj_id = ObjectId(rule_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    update_data = {k: v for k, v in rule_update.dict().items() if v is not None}
    if update_data:
        update_data["updated_at"] = datetime.utcnow()

    result = await rules_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found")

    updated_rule = await rules_collection.find_one({"_id": obj_id})
    return convert_mongo_to_response(updated_rule)


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: str,
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Delete a rule"""
    try:
        obj_id = ObjectId(rule_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    result = await rules_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rule not found")

    return {"message": "Rule deleted successfully"}


@router.post("/rules/{rule_id}/toggle")
async def toggle_rule(
    rule_id: str,
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Enable/disable a rule"""
    try:
        obj_id = ObjectId(rule_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    rule = await rules_collection.find_one({"_id": obj_id})
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    new_enabled_status = not rule.get("enabled", True)

    await rules_collection.update_one(
        {"_id": obj_id},
        {"$set": {"enabled": new_enabled_status, "updated_at": datetime.utcnow()}}
    )

    return {"message": f"Rule {'enabled' if new_enabled_status else 'disabled'} successfully"}


@router.post("/rules/evaluate")
async def evaluate_all_rules(
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Manually trigger rule evaluation"""
    enabled_rules = await rules_collection.find({"enabled": True}).to_list(length=None)
    results = await evaluate_rules(enabled_rules)

    return {
        "message": "Rule evaluation completed",
        "rules_evaluated": len(enabled_rules),
        "alerts_triggered": len(results)
    }


@router.get("/rules/history/{rule_id}")
async def get_rule_history(
    rule_id: str,
    skip: int = 0,
    limit: int = 20,
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Get rule trigger history"""
    try:
        obj_id = ObjectId(rule_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid rule ID")

    rule = await rules_collection.find_one({"_id": obj_id})
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return {
        "rule_id": rule_id,
        "rule_name": rule.get("name"),
        "triggered_count": rule.get("triggered_count", 0),
        "last_triggered": rule.get("last_triggered"),
        "history": []  # TODO: Implement actual history tracking
    }