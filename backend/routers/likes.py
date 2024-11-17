from fastapi import APIRouter, HTTPException, Depends, status
from models.like import LikeCreate, LikeResponse
from models.post import PostResponse
from utils.auth import get_current_user
from services.database import likes_collection, posts_collection
from bson import ObjectId
from pymongo.errors import PyMongoError

router = APIRouter()

@router.post("/", response_model=LikeResponse)
async def create_like(like: LikeCreate, user: dict = Depends(get_current_user)):
    try:
        # Check if the like already exists (user cannot like the same post twice)
        existing_like = await likes_collection.find_one({
            "post_id": like.post_id,
            "user_id": user["username"]
        })
        if existing_like:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already liked this post")

        # Insert the like into the collection
        like_dict = like.model_dump()
        like_dict["user_id"] = user["username"]
        result = await likes_collection.insert_one(like_dict)

        # Update the likes count in the corresponding post
        await posts_collection.update_one(
            {"_id": ObjectId(like.post_id)},
            {"$inc": {"likes_count": 1}}
        )

        return LikeResponse(**like_dict, id=str(result.inserted_id))
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{like_id}", response_model=LikeResponse)
async def delete_like(like_id: str, user: dict = Depends(get_current_user)):
    try:
        # Find the like entry
        like = await likes_collection.find_one({"_id": ObjectId(like_id)})
        if not like:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")
        if like["user_id"] != user["username"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot remove this like")

        # Delete the like entry
        await likes_collection.delete_one({"_id": ObjectId(like_id)})

        # Decrease the likes count in the corresponding post
        await posts_collection.update_one(
            {"_id": ObjectId(like["post_id"])},
            {"$inc": {"likes_count": -1}}
        )

        return LikeResponse(**like)
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/post/{post_id}", response_model=list[LikeResponse])
async def get_likes_for_post(post_id: str):
    try:
        # Retrieve all likes for a given post
        likes = await likes_collection.find({"post_id": post_id}).to_list(length=100)
        return [LikeResponse(**like) for like in likes]
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
