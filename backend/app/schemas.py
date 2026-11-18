from typing import Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    TypeAdapter,
    field_validator,
    model_validator,
)

Role = Literal["VOLUNTEER", "ORGANIZER"]
Status = Literal["DRAFT", "PUBLISHED", "ARCHIVED"]
Category = Literal["ANIMALS", "ECOLOGY", "SOCIAL", "CULTURE", "EDUCATION"]


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, from_attributes=True)


class Credentials(Schema):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower()


class Register(Credentials):
    password: str = Field(min_length=10, max_length=128)
    name: str = Field(min_length=1, max_length=100)
    role: Role
    organization_name: str | None = Field(default=None, min_length=1, max_length=160)

    @model_validator(mode="after")
    def organization_required(self):
        if self.role == "ORGANIZER" and not self.organization_name:
            raise ValueError("Укажите название организации")
        if self.role == "VOLUNTEER":
            self.organization_name = None
        return self


class ProfilePatch(Schema):
    name: str = Field(min_length=1, max_length=100)
    organization_name: str | None = Field(default=None, min_length=1, max_length=160)
    city: str = Field(default="", max_length=100)
    description: str = Field(default="", max_length=5000)
    skills: str = Field(default="", max_length=1000)
    interests: str = Field(default="", max_length=1000)
    website: str = Field(default="", max_length=2000)
    avatar_url: str = Field(default="", max_length=2000)

    @field_validator("website", "avatar_url")
    @classmethod
    def safe_url(cls, value):
        if value:
            TypeAdapter(HttpUrl).validate_python(value)
        return value


class ProjectInput(Schema):
    title: str = Field(min_length=1, max_length=160)
    city: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=300)
    starts_at: AwareDatetime
    duration: int = Field(ge=1, le=10000)
    duration_unit: Literal["HOURS", "DAYS", "WEEKS", "MONTHS"]
    description: str = Field(min_length=1, max_length=10000)
    category: Category
    cover_url: HttpUrl

    @field_validator("cover_url")
    @classmethod
    def cover_url_length(cls, value):
        if len(str(value)) > 2000:
            raise ValueError("Ссылка на обложку не должна превышать 2000 символов")
        return value


class StatusInput(Schema):
    status: Status
