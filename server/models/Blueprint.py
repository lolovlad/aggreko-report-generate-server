from datetime import datetime

from pydantic import BaseModel, UUID4, field_serializer, computed_field
from .Mixins import DeleteMixinModel, SystemVariablesMixin
from ..settings import settings


class TypeBlueprintModel(SystemVariablesMixin):
    pass


class TypeEquipmentBlueprintModel(SystemVariablesMixin):
    pass


class BaseBlueprint(BaseModel):
    name: str
    id_plant: int
    id_type: int

    path_template_docx_file: str
    path_map_data_json_file: str
    path_form_xlsx_file: str

    last_datetime_edit: datetime


class GetBlueprint(BaseBlueprint):
    uuid: UUID4

    type: TypeBlueprintModel
    plant: TypeEquipmentBlueprintModel

    @computed_field
    @property
    def download_link(self) -> str:
        m = self.path_form_xlsx_file.replace("\\", "/")
        return f"http://{settings.host_server}:{settings.port_server}/v1/file/?name_file=blueprint/{m}"

    @computed_field
    @property
    def download_link_docx(self) -> str:
        m = self.path_template_docx_file.replace("\\", "/")
        return f"http://{settings.host_server}:{settings.port_server}/v1/file/?name_file=blueprint/{m}"

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID4, _info):
        return str(uuid)
