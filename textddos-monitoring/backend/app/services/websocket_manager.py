import asyncio
from typing import Dict, Any, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
import json
from datetime import datetime   # ← Thêm dòng này
from app.core.config import settings
from bson import ObjectId   # ← Thêm import này

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.max_connections = settings.WS_MAX_CONNECTIONS

    async def connect(self, websocket: WebSocket):
        """Accept and add a new WebSocket connection"""
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008)  # Policy violation
            return

        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast_flow(self, flow_data: Dict[str, Any]):
            """Broadcast flow data to all connected clients"""
            
            
            # Làm sạch dữ liệu trước khi broadcast
            cleaned_data = self._clean_for_json(flow_data)
            
            logger.info("📤 Broadcasting flow data: {}", cleaned_data)

            message = {
                "type": "flow",
                "data": cleaned_data
            }
            await self._broadcast(message)
    def _clean_for_json(self, obj):
        """Chuyển các kiểu dữ liệu không JSON serializable thành string"""
        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items()}
        
        elif isinstance(obj, list):
            return [self._clean_for_json(item) for item in obj]
        
        elif isinstance(obj, datetime):
            return obj.isoformat()
        
        elif isinstance(obj, ObjectId):           # ← Xử lý ObjectId
            return str(obj)
        
        else:
            return obj

    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast alert data to all connected clients"""
        message = {
            "type": "alert",
            "data": alert_data
        }
        await self._broadcast(message)

    async def broadcast_stats(self, stats_data: Dict[str, Any]):
        """Broadcast statistics data to all connected clients"""
        message = {
            "type": "stats",
            "data": stats_data
        }
        await self._broadcast(message)

    async def broadcast(self, message: str):
        """Broadcast a raw message to all connected clients"""
        message_data = {"type": "message", "data": message}
        await self._broadcast(message_data)

    async def _broadcast(self, message: Dict[str, Any]):
            """Internal broadcast method"""
            if not self.active_connections:
                return

            connections = self.active_connections.copy()
            disconnected = []

            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to WebSocket: {e}")
                    disconnected.append(connection)

            # Cleanup disconnected connections
            for conn in disconnected:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)

    async def close_all(self):
        """Close all WebSocket connections"""
        connections = self.active_connections.copy()
        self.active_connections.clear()

        for connection in connections:
            try:
                await connection.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")

        logger.info("All WebSocket connections closed")

    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
