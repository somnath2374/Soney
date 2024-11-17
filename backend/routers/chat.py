from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from utils.auth import get_current_user
from fastapi.middleware.cors import CORSMiddleware
from services.database import users_collection, chats_collection
from models.chat import ChatMessage, ChatCreate, ChatResponse
from models.user import UserResponse
from typing import List
from bson import ObjectId
from datetime import datetime
import json
import asyncio
import logging

ws = FastAPI()

ws.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Or specify specific methods like ["GET", "POST"]
    allow_headers=["*"],  # Or specify specific headers
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
active_connections = {}

@ws.websocket("/chat/{receiver_id}/{token}")
async def websocket_chat(websocket: WebSocket, receiver_id: str, token: str):
    await websocket.accept()
    
    if not token:
        logging.warning("Token missing")
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail="Token missing")
    
    logging.debug(f"Received token: {token}")
    user = await get_current_user(token)
    if not user:
        logging.warning("Invalid token")
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail="Invalid token")

    active_connections[user.username] = websocket
    logging.debug(f"WebSocket connection added: {len(active_connections)} active connections")

    try:
        while True:
            data = await websocket.receive_text()
            chat_message = ChatMessage(
                sender_id=user.username,
                receiver_id=receiver_id,
                message=data,
                timestamp=datetime.utcnow()
            )
            await chats_collection.insert_one(chat_message.dict(by_alias=True))
            if receiver_id in active_connections:
                await active_connections[receiver_id].send_text(json.dumps(chat_message.dict(by_alias=True)))
    except WebSocketDisconnect:
        if user.username in active_connections:
            del active_connections[user.username]
        logging.debug(f"WebSocket connection closed: {len(active_connections)} remaining")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        if user.username in active_connections:
            del active_connections[user.username]
        await websocket.close(code=1011)

@router.get("/messages/{friend_id}", response_model=List[ChatResponse])
async def get_messages(friend_id: str, user: UserResponse = Depends(get_current_user)):
    messages = await chats_collection.find({
        "$or": [
            {"sender_id": user.username, "receiver_id": friend_id},
            {"sender_id": friend_id, "receiver_id": user.username}
        ]
    }).sort("timestamp", 1).to_list(100)
    return [ChatResponse(**message, id=str(message["_id"])) for message in messages]

@router.post("/messages", response_model=ChatResponse)
async def send_message(chat_create: ChatCreate, user: UserResponse = Depends(get_current_user)):
    mes_dict = chat_create.model_dump()
    mes_dict["sender_id"] = user.username
    mes_dict["timestamp"] = datetime.utcnow()
    mes_dict["read"] = False
    result = await chats_collection.insert_one(mes_dict)
    if chat_create.receiver_id in active_connections:
        mes_dict["timestamp"] = mes_dict["timestamp"].isoformat()
        mes_dict.pop("_id", None)
        await active_connections[chat_create.receiver_id].send_text(json.dumps(mes_dict))
    return ChatResponse(**mes_dict, id=str(result.inserted_id))
