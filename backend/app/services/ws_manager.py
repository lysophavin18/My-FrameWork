"""WebSocket connection manager for streaming progress updates."""

from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._scan_connections: dict[int, list[WebSocket]] = defaultdict(list)
        self._session_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect_scan(self, scan_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._scan_connections[scan_id].append(websocket)

    async def connect_session(self, session_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._session_connections[session_id].append(websocket)

    def disconnect_scan(self, scan_id: int, websocket: WebSocket) -> None:
        if websocket in self._scan_connections[scan_id]:
            self._scan_connections[scan_id].remove(websocket)

    def disconnect_session(self, session_id: int, websocket: WebSocket) -> None:
        if websocket in self._session_connections[session_id]:
            self._session_connections[session_id].remove(websocket)

    async def broadcast_scan(self, scan_id: int, payload: dict) -> None:
        for ws in list(self._scan_connections.get(scan_id, [])):
            await ws.send_json(payload)

    async def broadcast_session(self, session_id: int, payload: dict) -> None:
        for ws in list(self._session_connections.get(session_id, [])):
            await ws.send_json(payload)


ws_manager = ConnectionManager()
