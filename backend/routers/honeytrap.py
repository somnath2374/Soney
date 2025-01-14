import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from models.honeytrap import HoneytrapCreate, HoneytrapResponse
from services.database import honeytraps_collection, users_collection, logs_collection, detected_collection
from utils.auth import get_current_user
from typing import List
from routers.automate import *
from routers.chatbot import generate_realistic_email, generate_realistic_username

router = APIRouter()

logging.basicConfig(level=logging.INFO)

@router.post("/create", response_model=HoneytrapResponse)
async def create_honeytrap(honeytrap: HoneytrapCreate, background_tasks: BackgroundTasks):
    try:
        username = await generate_realistic_username(honeytrap.purpose)
        email = await generate_realistic_email(username)
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
    
@router.get("/detected", response_model=List[dict])
async def get_detected_users():
    try:
        detected_users = await detected_collection.find().to_list(length=100)
        for user in detected_users:
            user["_id"] = str(user["_id"])
        return detected_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/statistics")
async def get_honeytrap_statistics():
    try:
        honeytrap_usernames = [honeytrap["username"] for honeytrap in await honeytraps_collection.find().to_list(length=1000)]
        
        total_honeytraps = await honeytraps_collection.count_documents({})
        total_interactions = await logs_collection.count_documents({"username": {"$in": honeytrap_usernames}})
        total_posts = await posts_collection.count_documents({"author_id": {"$in": honeytrap_usernames}})
        total_likes = await posts_collection.aggregate([
            {"$match": {"author_id": {"$in": honeytrap_usernames}}},
            {"$group": {"_id": None, "total_likes": {"$sum": "$likes_count"}}}
        ]).to_list(length=1)
        total_comments = await posts_collection.aggregate([
            {"$match": {"author_id": {"$in": honeytrap_usernames}}},
            {"$group": {"_id": None, "total_comments": {"$sum": "$comments_count"}}}
        ]).to_list(length=1)
        total_friend_requests = await logs_collection.count_documents({"username": {"$in": honeytrap_usernames}, "action": {"$regex": "Sent friend request"}})
        total_detected_users = await detected_collection.count_documents({})

        most_active_honeytrap = await logs_collection.aggregate([
            {"$match": {"username": {"$in": honeytrap_usernames}}},
            {"$group": {"_id": "$username", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]).to_list(length=1)
        most_liked_post = await posts_collection.find({"author_id": {"$in": honeytrap_usernames}}).sort("likes_count", -1).limit(1).to_list(length=1)
        most_commented_post = await posts_collection.find({"author_id": {"$in": honeytrap_usernames}}).sort("comments_count", -1).limit(1).to_list(length=1)

        statistics = [
            {"name": "Total Honeytraps", "value": total_honeytraps},
            {"name": "Total Interactions", "value": total_interactions},
            {"name": "Total Posts by Honeytraps", "value": total_posts},
            {"name": "Total Likes on Honeytrap Posts", "value": total_likes[0]["total_likes"] if total_likes else 0},
            {"name": "Total Comments on Honeytrap Posts", "value": total_comments[0]["total_comments"] if total_comments else 0},
            {"name": "Total Friend Requests Sent by Honeytraps", "value": total_friend_requests},
            {"name": "Total Detected Users", "value": total_detected_users},
            {"name": "Most Active Honeytrap", "value": most_active_honeytrap[0]["_id"] if most_active_honeytrap else "N/A"},
            {"name": "Most Liked Honeytrap Post", "value": most_liked_post[0]["title"] if most_liked_post else "N/A"},
            {"name": "Most Commented Honeytrap Post", "value": most_commented_post[0]["title"] if most_commented_post else "N/A"},
        ]

        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
schedule_analysis()