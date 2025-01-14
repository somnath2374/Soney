from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from utils.auth import get_current_user
from services.database import users_collection, chats_collection, analysis_collection, detected_collection
from models.chat import ChatMessage, ChatCreate, ChatResponse
from models.user import UserResponse
from typing import List
from bson import ObjectId
from datetime import datetime
from routers.chatbot import generate_conversation, is_user_genuine
import json
import asyncio
import logging
from routers.chatbot import generate_conversation, is_user_genuine

# Add new collection for analysis

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

async def get_typing_delay(message: str) -> float:
    # Simple delay: 1 second per 20 characters
    return len(message) / 40

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
            message_data = json.loads(data)  # Parse the JSON string to a dictionary

            chat_message = ChatMessage(
                sender_id=user.username,
                receiver_id=receiver_id,
                message=message_data['message'],
                timestamp=datetime.utcnow()  # Set the timestamp here
            )
            result = await chats_collection.insert_one(chat_message.dict(by_alias=True, exclude={"id"}))
            chat_message.id = str(result.inserted_id)  # Set the id field correctly
            chat_message_dict = chat_message.dict(by_alias=True)
            chat_message_dict["timestamp"] = chat_message_dict["timestamp"].isoformat()  # Convert datetime to string
            if receiver_id in active_connections:
                await active_connections[receiver_id].send_text(json.dumps(chat_message_dict))
            
            # Check if there's an ongoing analysis
            analysis = await analysis_collection.find_one({
                "user_id": receiver_id,
                "friend_id": user.username,
                "status": "ongoing"
            })
            
            if analysis:
                # Update conversation history
                analysis["conversation_history"].append({
                    "is_user": True,
                    "message": message_data["message"]
                })
                
                # Generate AI response
                ai_response = generate_conversation(
                    message_data["message"],
                    analysis["conversation_history"]
                )
                
                # Add AI response to history
                analysis["conversation_history"].append({
                    "is_user": False,
                    "message": ai_response
                })
                delay = await get_typing_delay(ai_response)
                await asyncio.sleep(delay)
                # Check if enough exchanges for analysis
                if len(analysis["conversation_history"]) >= 10:
                    is_genuine = is_user_genuine(str(analysis["conversation_history"]))
                    analysis["result"] = is_genuine
                    analysis["status"] = "completed"
                
                await analysis_collection.update_one(
                    {"_id": analysis["_id"]},
                    {"$set": analysis}
                )
                
                # Send AI response
                ai_message = {
                    "sender_id": receiver_id,
                    "receiver_id": user.username,
                    "message": ai_response,
                    "timestamp": datetime.utcnow().isoformat(),
                    "is_ai": True
                }
                await active_connections[receiver_id].send_text(json.dumps(ai_message))
                await websocket.send_text(json.dumps(ai_message))
    except WebSocketDisconnect:
        if user.username in active_connections:
            del active_connections[user.username]
        logging.debug(f"WebSocket connection closed: {len(active_connections)} remaining")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        if user.username in active_connections:
            del active_connections[user.username]
        await websocket.close(code=1011)

@router.post("/analyze/{friend_id}")
async def start_analysis(friend_id: str, user: UserResponse = Depends(get_current_user)):
    conversation_history = []
    ai_message = generate_conversation("Hello!", conversation_history)
    
    analysis_session = {
        "user_id": user.username,
        "friend_id": friend_id,
        "conversation_history": conversation_history,
        "status": "ongoing",
        "timestamp": datetime.utcnow()
    }
    
    await analysis_collection.insert_one(analysis_session)
    
    # Send AI message through WebSocket
    if friend_id in active_connections:
        message = {
            "sender_id": user.username,
            "receiver_id": friend_id,
            "message": ai_message,
            "timestamp": datetime.utcnow().isoformat(),
            "is_ai": True,
        }
        await active_connections[friend_id].send_text(json.dumps(message))
        await active_connections[user.username].send_text(json.dumps(message))
    return {"status": "analysis_started"}

@router.get("/analyze/result/{friend_id}")
async def get_analysis_result(friend_id: str, user: UserResponse = Depends(get_current_user)):
    # Get the most recent completed analysis
    result = await analysis_collection.find_one({
        "user_id": user.username,
        "friend_id": friend_id,
        "status": "completed"
    }, sort=[("timestamp",-1)])
    
    if result and "result" in result:
        if result["result"] != "genuine":
            existing_record = await detected_collection.find_one({"username": friend_id})
            if existing_record:
                if "Spammy chat content" not in existing_record["reasons"]:
                    await detected_collection.update_one(
                        {"username": friend_id},
                        {"$push": {"reasons": f"Spammy chat content: detected as {result["result"]}"}}
                    )
            else:
                await detected_collection.insert_one({
                    "username": friend_id,
                    "reasons": [f"Spammy chat content: detected as {result["result"]}"],
                    "timestamp": datetime.utcnow().isoformat()
                })
        return {
            "is_genuine": result["result"],
            "conversation_count": await analysis_collection.count_documents({
                "user_id": user.username,
                "friend_id": friend_id,
                "status": "completed"
            })
        }
    
    return {"status": "no_analysis_found"}

@router.get("/detected-users")
async def get_detected_users():
    detected = await detected_collection.find(
        {},
        {"username": 1, "_id": 0}
    ).sort("timestamp", -1).to_list(1000)
    return detected

@router.get("/messages/{friend_id}", response_model=List[ChatResponse])
async def get_messages(friend_id: str, user: UserResponse = Depends(get_current_user)):
    messages = await chats_collection.find({
        "$or": [
            {"sender_id": user.username, "receiver_id": friend_id},
            {"sender_id": friend_id, "receiver_id": user.username}
        ]
    }).sort("timestamp", 1).to_list(100)
    return [ChatResponse(**message) for message in messages]

@router.post("/messages", response_model=ChatResponse)
async def send_message(chat_create: ChatCreate, user: UserResponse = Depends(get_current_user)):
    mes_dict = chat_create.model_dump()
    mes_dict["sender_id"] = user.username
    mes_dict["timestamp"] = datetime.utcnow()
    mes_dict["read"] = False
    result = await chats_collection.insert_one(mes_dict)
    mes_dict["_id"] = str(result.inserted_id)
    if chat_create.receiver_id in active_connections:
        mes_dict["timestamp"] = mes_dict["timestamp"].isoformat()  # Convert datetime to string
        await active_connections[chat_create.receiver_id].send_text(json.dumps(mes_dict))
    return ChatResponse(**mes_dict, id=str(result.inserted_id))


ws.include_router(router)
