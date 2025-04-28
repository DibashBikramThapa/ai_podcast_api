from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from utils.enum import AI_Model
from utils import settings

from core.podcast import AI_Podcast
from core.schema import PodcastQuery

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,  # Use the list here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/podcast")
def read_item(podcast_q:PodcastQuery):
    try:
        payload= {
            'user_prompt': podcast_q.user
        }
        ai_podcast =AI_Podcast(payload=payload, model=AI_Model.AI_ML.value)
        resp = ai_podcast.start()
        return {
                "message": "AI message received",
                "data": resp
                }
    except Exception as e:
        return JSONResponse(status_code=500, content=str(e))
