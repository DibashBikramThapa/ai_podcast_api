from pydantic import BaseModel


class PodcastQuery(BaseModel):
    user: str