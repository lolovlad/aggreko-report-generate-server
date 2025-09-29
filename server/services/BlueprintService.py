from fastapi import Depends, UploadFile, HTTPException, status

from ..repositories import FileBucketRepository, BlueprintRepository
from ..models.Blueprint import GetBlueprint
from ..tables import Blueprint

from untils.FileParser.ParserTempalteFile import ParserTemplateFile
from untils.FileBuilder.BuilderXlsxFile import BuilderXlsxFile
from untils.FileBuilder.BuilderDocxFile import BuilderDocxFile
from untils.FileParser.ParserFormFile import ParserFormFile
from untils.FileParser.JsonFile import JsonFile
from untils.Models.Fileschame import FileSchemas

from docxtpl import DocxTemplate, InlineImage
from io import BytesIO
from datetime import datetime
from pathlib import Path

from secrets import choice
from string import ascii_letters, digits


class BlueprintService:
    def __init__(self, blueprint_repo: BlueprintRepository = Depends()):
        self.__blueprint_repo: BlueprintRepository = blueprint_repo
        self.__buket_repo: FileBucketRepository = FileBucketRepository("blueprint")
        self.__count_item: int = 20

    def __get_name_file(self, extend: str) -> str:
        res = ''.join(choice(ascii_letters + digits) for x in range(15))
        return f"{res}.{extend}"

    @property
    def count_item(self) -> int:
        return self.__count_item

    @count_item.setter
    def count_item(self, item):
        self.__count_item = item

    async def get_count_page(self) -> int:
        count_row = await self.__blueprint_repo.count_row()
        sub_page = 0
        if count_row % self.__count_item > 0:
            sub_page += 1
        return count_row // self.__count_item + sub_page

    async def get_page(self, num_page: int) -> list[GetBlueprint]:
        start = (num_page - 1) * self.__count_item
        entities = await self.__blueprint_repo.get_limit(start, self.__count_item)
        blueprints = [GetBlueprint.model_validate(entity, from_attributes=True) for entity in entities]
        return blueprints

    async def get_by_search_field(self, search_field: str):
        entities = await self.__blueprint_repo.get_by_search_field(
            search_field,
        )
        blueprints = [GetBlueprint.model_validate(entity, from_attributes=True) for entity in entities]
        return blueprints

    async def add_blueprint(self,
                            name: str,
                            id_type: int,
                            id_plant: int,
                            file: UploadFile):
        name_file_docx = self.__get_name_file("docx")
        name_file_exel = self.__get_name_file("xlsx")

        path_file_docx = Path(name, f"Шаблон_{name}.docx")
        path_file_json = Path(name, name_file_exel.split(".")[0] + ".json")
        path_file_exel = Path(name, f"Оснавная_таблица_{name}.xlsx")

        parser_template = ParserTemplateFile(file.file.read())
        parser_template.parser()

        buffer = BytesIO()
        parser_template.file.save(buffer)
        buffer.seek(0)

        await self.__buket_repo.upload_file(str(path_file_docx).replace('\\','/'),
                                            buffer.getvalue(),
                                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        builder_file = BuilderXlsxFile(path_file_exel, parser_template.file_schema)
        builder_file.build()

        buffer = BytesIO()
        builder_file.file_xlsx.save(buffer)
        buffer.seek(0)

        await self.__buket_repo.upload_file(str(path_file_exel).replace('\\','/'),
                                            buffer.getvalue(),
                                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        buffer = BytesIO()
        json_str = builder_file.schemas.model_dump_json(indent=2)
        buffer.write(json_str.encode("utf-8"))
        buffer.seek(0)

        await self.__buket_repo.upload_file(str(path_file_json).replace('\\','/'),
                                            buffer.getvalue(),
                                            "application/json")

        blueprint_model = Blueprint(
            name=name,
            id_plant=id_plant,
            id_type=id_type,
            path_template_docx_file=str(path_file_docx),
            path_map_data_json_file=str(path_file_json),
            path_form_xlsx_file=str(path_file_exel)
        )
        await self.__blueprint_repo.add(blueprint_model)

    async def upload_xlsx(self, uuid: str, file: UploadFile):
        blueprint = await self.__blueprint_repo.get_by_uuid(uuid)
        await self.__buket_repo.delete_file(blueprint.path_form_xlsx_file.replace("\\", "/"))
        await self.__buket_repo.upload_file(blueprint.path_form_xlsx_file.replace("\\", "/"),
                                            file.file.read(),
                                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    async def get_file_schemas(self, uuid: str) -> FileSchemas:
        blueprint = await self.__blueprint_repo.get_by_uuid(uuid)
        file_sc = await self.__buket_repo.get_file(blueprint.path_map_data_json_file.replace("\\", "/"))
        models = FileSchemas.model_validate_json(file_sc)
        for i in range(len(models.protocols)):
            models.protocols[i].tables = []
            models.protocols[i].system_table = {}
        return models

    async def upload_docx(self, uuid: str, file: UploadFile):
        blueprint = await self.__blueprint_repo.get_by_uuid(uuid)
        await self.__buket_repo.delete_file(blueprint.path_template_docx_file.replace("\\", "/"))
        await self.__buket_repo.upload_file(blueprint.path_template_docx_file.replace("\\", "/"),
                                            file.file.read(),
                                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    async def delete_bluprint(self, uuid_blueprint: str):
        blueprint = await self.__blueprint_repo.get_by_uuid(uuid_blueprint)
        blueprint.is_delite = True
        await self.__blueprint_repo.add(blueprint)
