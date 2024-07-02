from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import uvicorn
from datetime import datetime

from mutate import ConvexClient, DEPLOYMENT_URL, clear_table, run_tests, list_messages, remove_messages, scan_incompletes, send_message

# You'd typically import your database functions here
# from database import get_tracks, create_track, update_track, delete_track

app = FastAPI(title="Music Track Metadata API")

client = ConvexClient(DEPLOYMENT_URL)

# CORS middleware to allow cross-origin requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

# Pydantic models for request/response schemas
class TrackBase(BaseModel):
    title: str
    artist: str
    album: str
    duration: int  # duration in seconds
    genre: Optional[str] = None

class TrackCreate(TrackBase):
    pass

class Track(TrackBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Dependency for database connection (placeholder)
async def get_db():
    # In a real app, you'd set up and yield a database connection here
    yield None

@app.get("/clear")
async def clear():
    clear_table(client)
    return {"message": "Table cleared"}

@app.get("/test")
async def test() -> dict[str, str]:
    run_tests(client)
    return {"message": "Tests passed"}

@app.get("/list")
async def list_chat(clean: bool = False, list_all: bool = False, lastN: int = 5) -> str | dict[str, list]:
    messages = list_messages(client, list_all=list_all, lastN=lastN)
    cleaned_messages = []
    for message in messages:
        cleaned_messages.append({"author": message["author"], "content": message["body"]})
    # Create a message string that neatly formats messages with numerical indices
    message_string = "\n".join([f"{i+1}. {message['author']}: {message['content']}" for i, message in enumerate(cleaned_messages)])
    
    if clean:
        return message_string
    else:
        return {"messages": cleaned_messages}

@app.get("/send")
async def send(body: str, author: str = "Tan Python") -> dict[str, str]:
    send_message(client, author, body)
    return {"message": "Message sent"}

@app.get("/remove")
async def remove() -> dict[str, str]:
    remove_messages(client)
    return {"message": "Messages removed"}

@app.get("/scan")
async def scan() -> dict[str, str]:
    count = scan_incompletes(client)
    return {"message": f"Scanned {count} incomplete messages"}

@app.get("/", response_model=dict)
async def root() -> dict[str, str]:
    return {"message": "Welcome to the Music Track Metadata API"}

@app.get("/tracks", response_model=List[Track])
async def read_tracks(skip: int = 0, limit: int = 100, db = Depends(get_db)):
    # Placeholder for database query
    # tracks = await get_tracks(db, skip=skip, limit=limit)
    tracks = []  # Replace with actual data
    return tracks

@app.post("/tracks", response_model=Track, status_code=201)
async def create_track(track: TrackCreate, db = Depends(get_db)):
    # Placeholder for database insertion
    # db_track = await create_track(db, track)
    db_track = Track(id=1, created_at=datetime.now(), updated_at=datetime.now(), **track.dict())
    return db_track

@app.get("/tracks/{track_id}", response_model=Track)
async def read_track(track_id: int, db = Depends(get_db)):
    # Placeholder for database query
    # track = await get_track(db, track_id)
    track = None  # Replace with actual data
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return track

@app.put("/tracks/{track_id}", response_model=Track)
async def update_track(track_id: int, track: TrackCreate, db = Depends(get_db)):
    # Placeholder for database update
    # updated_track = await update_track(db, track_id, track)
    updated_track = None  # Replace with actual data
    if updated_track is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return updated_track

@app.delete("/tracks/{track_id}", response_model=dict)
async def delete_track(track_id: int, db = Depends(get_db)) -> dict[str, str]:
    # Placeholder for database deletion
    # success = await delete_track(db, track_id)
    success = True  # Replace with actual result
    if not success:
        raise HTTPException(status_code=404, detail="Track not found")
    return {"message": "Track deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8008, reload=True)