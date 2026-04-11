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
        teacher_ws = self.active_connections.get('teacher_01')
        if not teacher_ws:
            return
        try:
            await teacher_ws.send_json(message)
        except Exception:
            self.disconnect('teacher_01')

    async def notify_clients_by_prefix(self, client_prefix: str, message: dict):
        dead_clients = []
        for client_id, ws in self.active_connections.items():
            if not str(client_id).startswith(client_prefix):
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead_clients.append(client_id)

        for client_id in dead_clients:
            self.disconnect(client_id)

    async def notify_students(self, message: dict):
        await self.notify_clients_by_prefix('student_', message)


ws_manager = WSManager()