from fastapi import APIRouter, Depends, HTTPException, status
from models.user import UserResponse
from services.database import users_collection
from services.database import db
from utils.auth import get_current_user
from pymongo.errors import PyMongoError

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    try:
        user = await users_collection.find_one({"username": current_user.username})
        if user:
            return UserResponse(id=str(user["_id"]), username=user["username"], email=user["email"],friends=user.get("friends",[]), friend_requests=user.get("friend_requests",[]))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
