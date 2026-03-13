"""WebSocket endpoints for streaming scan and pipeline updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.ws_manager import ws_manager

router = APIRouter()


@router.websocket("/scans/{scan_id}")
async def scan_ws(websocket: WebSocket, scan_id: int):
    await ws_manager.connect_scan(scan_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_scan(scan_id, websocket)


@router.websocket("/hunting/{session_id}")
async def hunting_ws(websocket: WebSocket, session_id: int):
    await ws_manager.connect_session(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_session(session_id, websocket)
