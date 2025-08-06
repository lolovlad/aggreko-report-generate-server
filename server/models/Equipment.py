from pydantic import BaseModel, UUID4, field_serializer
from .Mixins import SystemVariablesMixin


from .User import UserGet


class TypeEquipmentModel(SystemVariablesMixin):
    code: str


class BaseEquipment(BaseModel):
    name: str
    id_type: int
    code: str | None
    description: str | None


class GetEquipment(BaseEquipment):
    uuid: UUID4
    type: TypeEquipmentModel

    @field_serializer("uuid")
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class PostEquipment(BaseEquipment):
    pass


class UpdateEquipment(BaseEquipment):
    pass
