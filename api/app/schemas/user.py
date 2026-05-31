from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    role: str = Field(default="member", pattern="^(admin|member)$")
    is_active: bool = True
    hours_per_week: float = Field(ge=0.0, default=0.0)
    pages_per_week: int = Field(ge=0, default=0)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=8)
    role: str | None = Field(default=None, pattern="^(admin|member)$")
    is_active: bool | None = None
    hours_per_week: float | None = Field(default=None, ge=0.0)
    pages_per_week: int | None = Field(default=None, ge=0)


class UserSelfUpdate(BaseModel):
    email: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=8)
    hours_per_week: float | None = Field(default=None, ge=0.0)
    pages_per_week: int | None = Field(default=None, ge=0)
