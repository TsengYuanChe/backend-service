from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    account_name: str
    is_active: bool