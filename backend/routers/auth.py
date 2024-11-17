from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import UserCreate, UserResponse
from utils.auth import get_password_hash, verify_password, create_access_token
from services.database import users_collection
from pymongo.errors import PyMongoError

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def register(user: UserCreate):
    try:
        existing_user = await users_collection.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
        
        user_dict = user.model_dump()
        user_dict["hashed_password"] = get_password_hash(user.password)
        del user_dict["password"]
        user_dict["friends"] = []
        user_dict["friend_requests"] = []
        result = await users_collection.insert_one(user_dict)
        return UserResponse(**user_dict, id=str(result.inserted_id))
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await users_collection.find_one({"username": form_data.username})
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user["username"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
