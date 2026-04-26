from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
