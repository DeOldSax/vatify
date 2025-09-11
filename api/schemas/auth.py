from pydantic import BaseModel, EmailStr

class RegisterIn(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginIn(BaseModel):
    email_or_username: str
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    plan: str
    email_verified: bool
