from pydantic import BaseModel
from datetime import datetime


class ChatResponse(BaseModel):
    id: str
    id_atividade: str
    criador: str
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
