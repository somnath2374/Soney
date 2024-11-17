from fastapi import APIRouter, HTTPException, Depends
from utils.auth import get_current_user
from services.database import users_collection
from pymongo.errors import PyMongoError
from models.user import UserResponse
from bson import ObjectId
from typing import List

router = APIRouter()

@router.post("/send_request/{friend_id}")
async def send_friend_request(friend_id: str, user: UserResponse = Depends(get_current_user)):
    # Add debug logging to see what's happening
    print(f"Friend ID: {friend_id}")
    print(f"Current user: {user}")
    
    try:
        friend = await users_collection.find_one({"username": friend_id})
        print(f"Found friend: {friend}")  # Check if friend is found
        
        if not friend:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.username in friend["friend_requests"]:
            raise HTTPException(status_code=400, detail="Friend request already sent")
            
        await users_collection.update_one(
            {"username": friend_id},
            {"$push": {"friend_requests": user.username}}
        )
        return {"message": "Friend request sent"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error details: {str(e)}")


@router.post("/accept_request/{friend_id}")
async def accept_friend_request(friend_id: str, user: UserResponse = Depends(get_current_user)):
    try:
        # Debug prints
        print(f"Friend ID received: {friend_id}")
        print(f"Current user: {user}")
        
        friend = await users_collection.find_one({"username": friend_id})
        print(f"Found friend: {friend}")
        
        if not friend:
            raise HTTPException(status_code=404, detail="User not found")
            
        if friend_id not in user.friend_requests:
            raise HTTPException(status_code=400, detail="No friend request from this user")
            
        # Update friend document
        await users_collection.update_one(
            {"username": user.username},
            {
                "$pull": {"friend_requests": friend_id},
                "$addToSet": {"friends": friend_id}
            }
        )
        
        # Update current user document
        await users_collection.update_one(
            {"username": friend_id},
            {"$addToSet": {"friends": user.username}}
        )
        
        return {"message": "Friend request accepted"}
        
    except Exception as e:
        print(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/reject_request/{friend_id}")
async def reject_friend_request(friend_id: str, user: UserResponse = Depends(get_current_user)):
    try:
        friend = await users_collection.find_one({"username": friend_id})
        if not friend:
            raise HTTPException(status_code=404, detail="User not found")
        if friend_id not in user.friend_requests:
            raise HTTPException(status_code=400, detail="No friend request from this user")
        await users_collection.update_one(
            {"username": user.username },
            {"$pull": {"friend_requests": friend_id}}
        )
        return {"message": "Friend request rejected"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=List[str])
async def get_friends(user_id: str):
    try:
        user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        return user_data["friends"]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))