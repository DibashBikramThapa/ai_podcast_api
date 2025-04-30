from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from utils.enum import AI_Model
from utils import settings

from core.podcast import AI_Podcast
from core.schema import PodcastQuery, PersonalityUpdate, PersonalityBulkUpdate
from core.summarizer import AI_Summarizer
from utils.personality_manager import PersonalityManager

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize personality manager
personality_manager = PersonalityManager()

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

@app.get("/summarize-page")
def summarize_page(request: Request):
    """Serve the summarization page"""
    return templates.TemplateResponse("summarize.html", {"request": request})

@app.post("/summarize")
def summarize(podcast_q: PodcastQuery):
    try:
        payload = {
            'user_prompt': podcast_q.user
        }
        ai_summarizer = AI_Summarizer(payload=payload)
        individual_responses, combined_response = ai_summarizer.start()
        return {
                "message": "Summarization completed",
                "individual_responses": individual_responses,
                "combined_response": combined_response
                }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/admin")
def admin_page(request: Request):
    """Serve the admin configuration page"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/api/personalities")
def get_personalities():
    """Get all model personalities"""
    return personality_manager.get_personalities()

@app.post("/api/personalities/update")
def update_personality(update: PersonalityUpdate):
    """Update a single model's personality"""
    success = personality_manager.update_personality(update.model_id, update.personality)
    return {"success": success}

@app.post("/api/personalities/update-all")
def update_all_personalities(update: PersonalityBulkUpdate):
    """Update all model personalities at once"""
    success = personality_manager.update_all_personalities(update.personalities)
    return {"success": success}

@app.post("/api/personalities/reset")
def reset_personalities():
    """Reset all personalities to defaults"""
    success = personality_manager.reset_to_defaults()
    return {"success": success}
