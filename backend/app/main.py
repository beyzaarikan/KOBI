from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import inventory, orders, operations
from app.services.ai_agent import support_agent
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Kobi App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(operations.router, prefix="/api/v1/operations", tags=["operations"])

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Broadcast error: {e}")

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Chatbot lojiğini çağır
            # Basit test için mock response döndür
            response = {"message": f"Server received: {data}"}
            await websocket.send_json(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "kobi-app-api"}
