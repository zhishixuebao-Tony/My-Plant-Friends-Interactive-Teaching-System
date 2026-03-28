from fastapi import WebSocket
from typing import Dict

class WSManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def notify_teacher(self, message: dict):
        """学生每按一次'下一步'，调用此方法让教师端无刷新更新统计图表"""
        teacher_ws = self.active_connections.get("teacher_01")
        if teacher_ws:
            await teacher_ws.send_json(message)

ws_manager = WSManager()