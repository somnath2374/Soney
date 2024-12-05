import random
import datetime
import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from models.honeytrap import HoneytrapCreate, HoneytrapResponse
from models.post import PostCreate, PostResponse
from services.database import honeytraps_collection, users_collection, posts_collection
from utils.auth import get_current_user
from bson import ObjectId
import string
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import List

router = APIRouter()
scheduler = AsyncIOScheduler()
scheduler.start()

logging.basicConfig(level=logging.INFO)

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_realistic_username():
    adjectives = ["cool", "fast", "smart", "bright", "dark"]
    nouns = ["lion", "tiger", "bear", "eagle", "shark"]
    return f"{random.choice(adjectives)}_{random.choice(nouns)}_{generate_random_string(4)}"

def generate_realistic_email():
    domains = ["example.com", "test.com", "demo.com"]
    return f"{generate_random_string(6)}@{random.choice(domains)}"

def generate_enticing_post_content():
    titles = [
        "Win a Free iPhone!",
        "Get Rich Quick with This Simple Trick",
        "Exclusive Offer: Limited Time Only",
        "Congratulations! You've Won a Prize",
        "Earn Money from Home Easily"
    ]
    contents = [
        "Click the link to claim your free iPhone now!",
        "Learn how to make thousands of dollars with minimal effort.",
        "Don't miss out on this exclusive offer. Act now!",
        "You've been selected to win a prize. Click here to claim it.",
        "Discover how you can earn money from the comfort of your home."
    ]
    return random.choice(titles), random.choice(contents)

async def create_enticing_post(username: str):
    title, content = generate_enticing_post_content()
    post_data = {
        "title": title,
        "content": content,
        "author_id": username,
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
        "likes_count": 0,
        "dislikes_count": 0,
        "comments_count": 0,
        "comments": [],
        "hashtags": [],
        "pictures": [],
        "videos": []
    }
    await posts_collection.insert_one(post_data)

async def get_random_honeytrap(exclude_username: str) -> str:
    honeytraps = await honeytraps_collection.find({"username": {"$ne": exclude_username}}).to_list(length=100)
    if not honeytraps:
        return None
    return random.choice(honeytraps)["username"]

async def send_friend_request(sender_username: str):
    receiver_username = await get_random_honeytrap(sender_username)
    if receiver_username:
        receiver = await users_collection.find_one({"username": receiver_username})
        if sender_username not in receiver["friend_requests"] and sender_username not in receiver["friends"]:
            await users_collection.update_one(
                {"username": receiver_username},
                {"$push": {"friend_requests": sender_username}}
            )
            logging.info(f"Friend request sent from {sender_username} to {receiver_username}")

async def accept_friend_request(username: str):
    user = await users_collection.find_one({"username": username})
    if user and user["friend_requests"]:
        friend_username = random.choice(user["friend_requests"])
        await users_collection.update_one(
            {"username": username},
            {"$pull": {"friend_requests": friend_username},
             "$addToSet": {"friends": friend_username}}
        )
        await users_collection.update_one(
            {"username": friend_username},
            {"$addToSet": {"friends": username}}
        )
        logging.info(f"Friend request from {friend_username} accepted by {username}")

def schedule_post_creation(username: str):
    for i in range(5):  # Schedule 5 posts
        delay = random.randint(1, 2)  # Delay between 1 and 2 minutes
        scheduler.add_job(create_enticing_post, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=delay), args=[username], misfire_grace_time=60)

def schedule_friend_requests(username: str):
    scheduler.add_job(send_friend_request, 'interval', minutes=1, args=[username], misfire_grace_time=60)
    scheduler.add_job(accept_friend_request, 'interval', minutes=2, args=[username], misfire_grace_time=60)

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

        # Schedule post creation and friend requests in the background
        background_tasks.add_task(schedule_post_creation, username)
        background_tasks.add_task(schedule_friend_requests, username)

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