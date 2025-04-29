from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from utils.enum import AI_Model
from utils import settings

from core.podcast import AI_Podcast
from core.schema import PodcastQuery

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,  # Use the list here
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def read_root(request: Request):
    """Serve the main podcast application page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/podcast")
def read_item(podcast_q: PodcastQuery):
    try:
        payload = {
            'user_prompt': podcast_q.user
        }
        ai_podcast = AI_Podcast(payload=payload, model=AI_Model.AI_ML.value)
        resp = ai_podcast.start()
        return {
                "message": "AI message received",
                "data": resp
                }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
