import asyncio
import json
from typing import Dict, List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

# Using the same redis pool config as analytics, simplified for the architecture demo
redis_pool = redis.ConnectionPool.from_url("redis://localhost:6379/0", decode_responses=True)
redis_client = redis.Redis(connection_pool=redis_pool)

router = APIRouter(prefix="/api/v1/ws", tags=["WebSockets"])

class ConnectionManagerSocket:
    """
    Manages active WebSocket connections per tenant.
    Allows broadcasting messages specific to a single company's dashboard.
    """
    def __init__(self):
        # Maps tenant_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect_ws(self, websocket: WebSocket, tenant_id: str):
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = []
        self.active_connections[tenant_id].append(websocket)
        print(f"WS Connected for tenant {tenant_id}. Total connections: {len(self.active_connections[tenant_id])}")

    def disconnect_ws(self, websocket: WebSocket, tenant_id: str):
        if tenant_id in self.active_connections:
            try:
                self.active_connections[tenant_id].remove(websocket)
                if not self.active_connections[tenant_id]:
                    del self.active_connections[tenant_id]
                print(f"WS Disconnected for tenant {tenant_id}")
            except ValueError:
                pass

    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """
        Sends a JSON payload to all connected clients arrayed under a tenant.
        """
        if tenant_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Failed to send to WS client: {e}")
                    dead_connections.append(connection)
            
            # Cleanup any broken pipes
            for dead in dead_connections:
                self.disconnect_ws(dead, tenant_id)

manager = ConnectionManagerSocket()

class EventBroadcaster:
    """
    Listens to a global Redis Pub/Sub channel for system events 
    and bridges them down to the correct WebSocket tenant channels.
    """
    @staticmethod
    async def listen_to_redis_events():
        print("Starting Redis PubSub EventBroadcaster loop...")
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("finance_system_events")
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        tenant_id = data.get("tenant_id")
                        if tenant_id:
                            # Forward the backend event up to the frontend UI!
                            await manager.broadcast_to_tenant(tenant_id, data)
                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        print(f"Error broadcasting event: {e}")
        except asyncio.CancelledError:
            print("Redis EventBroadcaster loop cancelled.")
        finally:
            await pubsub.unsubscribe("finance_system_events")

    @staticmethod
    async def broadcast_ocr_finished(tenant_id: str, invoice_id: str, status: str, details: str = ""):
        """
        Helper method to push an event INTO the Redis channel from anywhere in the app APIs/Celery.
        """
        payload = {
            "tenant_id": tenant_id,
            "event": "OCR_PROCESS_FINISHED",
            "invoice_id": invoice_id,
            "status": status,
            "message": details
        }
        try:
            await redis_client.publish("finance_system_events", json.dumps(payload))
        except Exception as e:
            print(f"Failed to publish to redis: {e}")

@router.websocket("/{tenant_id}")
async def websocket_endpoint(websocket: WebSocket, tenant_id: str):
    """
    Client connecting: ws://localhost:8000/api/v1/ws/{tenant_id}
    In production, you would authenticate the user first by getting the token from query params or headers,
    and verifying it belongs to this tenant_id.
    """
    await manager.connect_ws(websocket, tenant_id)
    try:
        while True:
            # We expect frontend might send pings or simple ACKs
            data = await websocket.receive_text()
            # Could echo or process data here if needed
    except WebSocketDisconnect:
        manager.disconnect_ws(websocket, tenant_id)
    except Exception as e:
        manager.disconnect_ws(websocket, tenant_id)
