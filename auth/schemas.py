from pydantic import BaseModel, EmailStr, field_validator 
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        if not re.findall('[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.findall('[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not re.findall('[0-9]', v):
            raise ValueError('Password must contain at least one digit.')
        if not re.findall('[^a-zA-Z0-9]', v):
            raise ValueError('Password must contain at least one special character (e.g., !, @, #, $).')
        return v

class UserRead(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: str
