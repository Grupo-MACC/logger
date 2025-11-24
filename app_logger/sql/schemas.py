from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal

class Message(BaseModel):
    detail: Optional[str] = Field(example="error or success message")