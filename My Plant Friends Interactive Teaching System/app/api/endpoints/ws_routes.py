from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.ws_manager import ws_manager

router = APIRouter()

@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(client_id, websocket)
    try:
        while True:
            await websocket.receive_text() # 保持心跳
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)