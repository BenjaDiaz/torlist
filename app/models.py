from pydantic import BaseModel

class IPAddress(BaseModel):
    ip: str
