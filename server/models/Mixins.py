from pydantic import BaseModel


class DeleteMixinModel(BaseModel):
    is_delite: bool


class SystemVariablesMixin(BaseModel):
    system_name: str
    name: str
    description: str | None
    id: int | None

