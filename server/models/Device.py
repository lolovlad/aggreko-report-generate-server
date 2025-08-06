from datetime import datetime

from pydantic import BaseModel
from .Mixins import SystemVariablesMixin


class TypeDeviceModel(SystemVariablesMixin):
    pass


class BaseDevice(BaseModel):
    name: str
    error: str
    code: str
    date_check_last: datetime
    date_check_next: datetime


class PostDevice(BaseDevice):
    id_type: int


class GetDevice(BaseDevice):
    id: int
    type: TypeDeviceModel
