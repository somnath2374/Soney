from fastapi import APIRouter, HTTPException, Depends
from models.honeytrap import HoneytrapCreate,HoneytrapResponse
from services.database import honeytraps_collection,users_collection
from utils.auth import get_current_user
import random
import string

router = APIRouter()

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_realistic_username():
    adjectives = ["cool", "fast", "smart", "bright", "dark"]
    nouns = ["lion", "tiger", "bear", "eagle", "shark"]
    return f"{random.choice(adjectives)}_{random.choice(nouns)}_{generate_random_string(4)}"

def generate_realistic_email():
    domains = ["example.com", "test.com", "demo.com"]
    return f"{generate_random_string(6)}@{random.choice(domains)}"

@router.post("/create", response_model=HoneytrapResponse)
async def create_honeytrap(honeytrap: HoneytrapCreate):
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
        return honeytrap_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def get_honeypots():
    try:
        honeypots = await honeytraps_collection.find().to_list(length=100)
        for honeypot in honeypots:
            honeypot["_id"] = str(honeypot["_id"])
        return honeypots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))