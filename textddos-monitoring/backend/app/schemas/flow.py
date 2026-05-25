from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Flow Schemas
class FlowBase(BaseModel):
    switch: str
    src_ip: str
    dst_ip: str
    protocol: str
    pktrate: float
    tot_kbps: float
    pktcount: int
    bytecount: int
    label: int
    confidence: float

class FlowCreate(FlowBase):
    additional_features: Optional[Dict[str, Any]] = {}

class FlowUpdate(BaseModel):
    label: Optional[int]
    confidence: Optional[float]
    additional_features: Optional[Dict[str, Any]]

class FlowResponse(FlowBase):
    id: str
    timestamp: datetime
    additional_features: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True

class FlowStats(BaseModel):
    total_flows: int
    attack_flows: int
    normal_flows: int
    attack_percentage: float
    top_attacking_ips: List[Dict[str, Any]]
    top_targeted_ips: List[Dict[str, Any]]

# Alert Schemas
class AlertBase(BaseModel):
    title: str
    description: str
    severity: str
    src_ip: str
    dst_ip: Optional[str]
    protocol: Optional[str]
    pktrate: float
    confidence: float

class AlertCreate(AlertBase):
    rule_triggered: Optional[str]

class AlertUpdate(BaseModel):
    status: Optional[str]
    actions_taken: Optional[List[str]]

class AlertResponse(AlertBase):
    id: str
    timestamp: datetime
    status: str
    rule_triggered: Optional[str]
    actions_taken: Optional[List[str]] = []

# Rule Schemas
class RuleBase(BaseModel):
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[str]

class RuleCreate(RuleBase):
    enabled: bool = True

class RuleUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    conditions: Optional[Dict[str, Any]]
    actions: Optional[List[str]]
    enabled: Optional[bool]

class RuleResponse(RuleBase):
    id: str
    enabled: bool
    created_at: datetime
    updated_at: datetime
    triggered_count: int
    last_triggered: Optional[datetime]

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_flows: int
    attack_flows: int
    normal_flows: int
    attack_percentage: float
    active_alerts: int
    active_rules: int

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]

class TopIP(BaseModel):
    ip: str
    count: int
