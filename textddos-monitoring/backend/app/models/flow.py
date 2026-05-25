from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class FlowModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    switch: str
    src_ip: str
    dst_ip: str
    protocol: str
    pktrate: float
    tot_kbps: float
    pktcount: int
    bytecount: int
    label: int  # 0=normal, 1=attack
    confidence: float
    additional_features: Optional[Dict[str, Any]] = {}

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "switch": "s1",
                "src_ip": "192.168.1.100",
                "dst_ip": "10.0.0.1",
                "protocol": "TCP",
                "pktrate": 450.0,
                "tot_kbps": 2340.0,
                "pktcount": 5000,
                "bytecount": 2500000,
                "label": 0,
                "confidence": 0.95
            }
        }

class AlertModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    title: str
    description: str
    severity: str  # critical, high, medium, low
    status: str = "new"  # new, acknowledged, resolved
    src_ip: str
    dst_ip: Optional[str]
    protocol: Optional[str]
    pktrate: float
    confidence: float
    rule_triggered: Optional[str]
    actions_taken: Optional[list] = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class RuleModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    conditions: Dict[str, Any]  # e.g., {"pktrate": {"gt": 1000}, "protocol": "UDP"}
    actions: list  # e.g., ["block_ip", "alert", "log"]
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    triggered_count: int = 0
    last_triggered: Optional[datetime]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
