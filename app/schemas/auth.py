from pydantic import BaseModel


class LoginRequest(BaseModel):
    account_name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    
