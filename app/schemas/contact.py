from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Annotated[str, Field(min_length=1, max_length=100)]
    phone: Annotated[str, Field(min_length=1, max_length=30)]
    email: EmailStr
    comment: Annotated[str, Field(min_length=1, max_length=2000)]

    @classmethod
    @field_validator("phone")
    def validate_phone(cls, value: str) -> str:
        allowed_symbols = set("+0123456789 ()-.")
        has_invalid_symbols = any(char not in allowed_symbols for char in value)
        has_wrong_plus_position = "+" in value[1:]

        if has_invalid_symbols or has_wrong_plus_position:
            raise ValueError("Phone number contains invalid symbols or has a '+' in the wrong position.")

        return value


class ContactResponse(BaseModel):
    request_id: str
    status: str
    message: str
