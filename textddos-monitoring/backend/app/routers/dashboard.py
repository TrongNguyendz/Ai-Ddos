from fastapi import APIRouter, HTTPException, Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection

from app.schemas.flow import DashboardStats, ChartData
from app.core.database import get_flows_collection, get_alerts_collection, get_rules_collection
from app.core.config import settings

router = APIRouter()

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection),
    alerts_collection: AsyncIOMotorCollection = Depends(get_alerts_collection),
    rules_collection: AsyncIOMotorCollection = Depends(get_rules_collection)
):
    """Get dashboard overview statistics"""
    from datetime import datetime, timedelta

    # Get recent flows (last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_flows = await flows_collection.find(
        {"timestamp": {"$gte": one_hour_ago}}
    ).to_list(length=None)

    total_flows = len(recent_flows)
    attack_flows = len([f for f in recent_flows if f.get("label") == 1])
    normal_flows = total_flows - attack_flows

    # Get active alerts
    active_alerts = await alerts_collection.count_documents({"status": {"$ne": "resolved"}})

    # Get active rules
    active_rules = await rules_collection.count_documents({"enabled": True})

    attack_percentage = (attack_flows / total_flows * 100) if total_flows > 0 else 0

    return DashboardStats(
        total_flows=total_flows,
        attack_flows=attack_flows,
        normal_flows=normal_flows,
        attack_percentage=round(attack_percentage, 2),
        active_alerts=active_alerts,
        active_rules=active_rules
    )

@router.get("/dashboard/charts/pktrate-kbps", response_model=ChartData)
async def get_pktrate_kbps_chart(
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection)
):
    """Get packet rate and kbps chart data for last 10 minutes"""
    from datetime import datetime, timedelta

    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

    # Aggregate data by minute
    pipeline = [
        {"$match": {"timestamp": {"$gte": ten_minutes_ago}}},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%H:%M",
                    "date": "$timestamp"
                }
            },
            "avg_pktrate": {"$avg": "$pktrate"},
            "avg_kbps": {"$avg": "$tot_kbps"}
        }},
        {"$sort": {"_id": 1}}
    ]

    results = await flows_collection.aggregate(pipeline).to_list(length=None)

    labels = [r["_id"] for r in results]
    pktrate_data = [round(r.get("avg_pktrate", 0), 2) for r in results]
    kbps_data = [round(r.get("avg_kbps", 0), 2) for r in results]

    return ChartData(
        labels=labels,
        datasets=[
            {
                "label": "Packet Rate (pps)",
                "data": pktrate_data,
                "borderColor": "#3b82f6",
                "backgroundColor": "rgba(59, 130, 246, 0.1)"
            },
            {
                "label": "Total Kbps",
                "data": kbps_data,
                "borderColor": "#10b981",
                "backgroundColor": "rgba(16, 185, 129, 0.1)"
            }
        ]
    )

@router.get("/dashboard/charts/normal-attack", response_model=ChartData)
async def get_normal_attack_chart(
    flows_collection: AsyncIOMotorCollection = Depends(get_flows_collection)
):
    """Get normal vs attack distribution chart"""
    from datetime import datetime, timedelta

    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    pipeline = [
        {"$match": {"timestamp": {"$gte": one_hour_ago}}},
        {"$group": {
            "_id": "$label",
            "count": {"$sum": 1}
        }}
    ]

    results = await flows_collection.aggregate(pipeline).to_list(length=None)

    normal_count = 0
    attack_count = 0

    for result in results:
        if result["_id"] == 0:
            normal_count = result["count"]
        elif result["_id"] == 1:
            attack_count = result["count"]

    return ChartData(
        labels=["Normal", "Attack"],
        datasets=[{
            "data": [normal_count, attack_count],
            "backgroundColor": ["#10b981", "#ef4444"],
            "borderColor": ["#064e3b", "#7f1d1d"],
            "borderWidth": 2
        }]
    )
