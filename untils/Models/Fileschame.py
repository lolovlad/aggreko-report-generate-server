from pydantic import BaseModel


class Workers(BaseModel):
    name: str = ""
    surname: str = ""
    patronymic: str = ""
    job_title: str = ""
    signature: str = ""


class Equipment(BaseModel):
    name: str
    type_equip: str
    error: str
    number: str
    certificate: str
    data_start: str
    data_end: str


class Size(BaseModel):
    width: int = 0
    height: int = 0


class CellSchemas(BaseModel):
    x: int
    y: int
    global_x: int = 0
    global_y: int = 0
    is_merge: bool = False
    is_data: bool = False
    text: str
    size: Size


class TableSchemas(BaseModel):
    cells: list[CellSchemas] = []


class Remark(BaseModel):
    note: str | None = None
    comment: str | None = None
    conclusion: str | None = None


class Protocol(BaseModel):
    name: str = ""
    tables: list[TableSchemas] = []
    list_equipment: list[Equipment] = []
    system_table: TableSchemas = None
    remark: Remark | None = Remark()


class FileSchemas(BaseModel):
    date: str = ""
    object: str = ""
    protocols: list[Protocol] = []
    list_workers: list[Workers] = []
