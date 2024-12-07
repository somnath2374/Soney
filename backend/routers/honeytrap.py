import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from models.honeytrap import HoneytrapCreate, HoneytrapResponse
from services.database import honeytraps_collection, users_collection, logs_collection
from utils.auth import get_current_user
from typing import List
from routers.automate import *

router = APIRouter()

logging.basicConfig(level=logging.INFO)

@router.post("/create", response_model=HoneytrapResponse)
async def create_honeytrap(honeytrap: HoneytrapCreate, background_tasks: BackgroundTasks):
    try:
        username = generate_realistic_username()
        email = generate_realistic_email()
        honeytrap_data = {
            "purpose": honeytrap.purpose,
            "username": username,
            "email": email,
            "friends": [],
            "friend_requests": []
        }
        result = await honeytraps_collection.insert_one(honeytrap_data)
        honeytrap_data["id"] = str(result.inserted_id)
        await users_collection.insert_one(honeytrap_data)  # Add to users collection as well

        # Schedule post creation, friend requests, and interactions in the background
        background_tasks.add_task(schedule_post_creation, username)
        background_tasks.add_task(schedule_friend_requests, username)
        background_tasks.add_task(schedule_interactions, username)

        return honeytrap_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[HoneytrapResponse])
async def get_honeypots():
    try:
        honeypots = await honeytraps_collection.find().to_list(length=100)
        for honeypot in honeypots:
            honeypot["id"] = str(honeypot.pop("_id"))
        return honeypots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/logs/{username}", response_model=List[dict])
async def get_honeytrap_logs(username: str):
    try:
        logs = await logs_collection.find({"username": username}).to_list(length=100)
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))