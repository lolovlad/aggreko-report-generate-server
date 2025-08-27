from pydantic import BaseModel, UUID4, field_serializer, computed_field
from .Mixins import SystemVariablesMixin
from .User import UserGet
from .Blueprint import GetBlueprint
from .Equipment import GetEquipment
from datetime import datetime
from ..settings import settings


class StateClaim(SystemVariablesMixin):
    pass


class BaseClaim(BaseModel):
    name: str | None
    datetime: datetime | None
    main_document: str | None
    edit_document: str | None
    comment: str | None
    last_datetime_edit: datetime
    blueprint: GetBlueprint | None


class GetClaim(BaseClaim):
    uuid: UUID4
    user: UserGet
    state_claim: StateClaim
    equipment: GetEquipment | None

    @computed_field
    @property
    def download_link_main(self) -> str:
        if self.main_document is not None:
            m = self.main_document.replace("\\", "/")
            return f"http://{settings.host_server}:{settings.port_server}/v1/file/?name_file=report/{m}"
        else:
            return None

    @computed_field
    @property
    def download_link_edit(self) -> str | None:
        if self.edit_document is not None:
            m = self.edit_document.replace("\\", "/")
            return f"http://{settings.host_server}:{settings.port_server}/v1/file/?name_file=report/{m}"
        else:
            return None

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)


class PostClaim(BaseModel):
    name: str
    uuid_blueprint: str
    uuid_equipment: str


class FullOneClaim(GetClaim):
    blueprint_xlsx_file: str | None
    blueprint_json_file: dict | None

    @computed_field
    @property
    def download_link_xlsx_blueprint(self) -> str | None:
        if self.blueprint_xlsx_file is not None:
            m = self.blueprint_xlsx_file.replace("\\", "/")
            return f"http://{settings.host_server}:{settings.port_server}/v1/file/?name_file=report/{m}"
        else:
            return None