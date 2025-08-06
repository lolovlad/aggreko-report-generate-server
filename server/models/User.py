from pydantic import BaseModel, UUID4, field_serializer
from datetime import datetime
from .Mixins import DeleteMixinModel, SystemVariablesMixin

from typing import Optional


class Profession(SystemVariablesMixin):
    pass


class TypeUser(SystemVariablesMixin):
    pass


class GetTypeUser(TypeUser):
    id: int


class UserBase(BaseModel):
    email: str | None
    id_type: int
    name: str | None
    surname: str | None
    patronymic: str | None
    id_profession: int | None
    painting: Optional[str | None] = None


class UserGet(UserBase):
    uuid: UUID4
    type: GetTypeUser
    profession: Profession | None

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class UserPost(UserBase):
    password: str


class UserUpdate(UserBase):
    password: str | None = None
