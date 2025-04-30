from pydantic import BaseModel
from typing import Dict


class PodcastQuery(BaseModel):
    user: str


class PersonalityUpdate(BaseModel):
    model_id: str
    personality: str


class PersonalityBulkUpdate(BaseModel):
    personalities: Dict[str, str]