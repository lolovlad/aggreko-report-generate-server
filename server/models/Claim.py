from pydantic import BaseModel, UUID4, field_serializer, computed_field
from .Mixins import SystemVariablesMixin
from .User import UserGet
from datetime import datetime
from ..settings import settings


class StateClaim(SystemVariablesMixin):
    pass


class BaseClaim(BaseModel):
    datetime: datetime
    main_document: str | None
    edit_document: str | None
    comment: str | None
    last_datetime_edit: datetime


class GetClaim(BaseClaim):
    uuid: UUID4
    user: UserGet
    state_claim: StateClaim

    @computed_field
    @property
    def download_link_main(self) -> str:
        m = self.main_document.replace("\\", "/")
        return f"http://{settings.host_server}:{settings.port_server}/v1/file/?name_file=report/{m}"

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