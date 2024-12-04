from fastapi import FastAPI, WebSocket
from routers import auth, post, comment, likes, chat,user,friends,honeytrap
from starlette.middleware.cors import CORSMiddleware
import logging,asyncio
from routers.chat import ws

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Or specify specific methods like ["GET", "POST"]
    allow_headers=["*"],  # Or specify specific headers
)

app.mount("/ws", ws)
# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(post.router, prefix="/post", tags=["Posts"])
app.include_router(comment.router, prefix="/comments", tags=["Comments"])
app.include_router(likes.router, prefix="/likes", tags=["Likes"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(friends.router, prefix="/friends", tags=["Friends"])
app.include_router(honeytrap.router, prefix="/honeytrap", tags=["Honeytrap"])

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

