from fastapi import Depends, UploadFile

from ..repositories import ClaimRepository, UserRepository, BlueprintRepository, FileBucketRepository, EnvRepository, EquipmentRepository
from ..models.Claim import *
from ..tables import Claim, Blueprint
from .BlueprintService import BlueprintService

from untils.Models.Fileschame import FileSchemas
from untils.FileParser.ParserFormFile import ParserFormFile
from untils.FileParser.XlsxFile import XlsxFile
from untils.FileBuilder.BuilderDocxFile import BuilderDocxFile

from json import loads

from secrets import choice
from string import ascii_letters, digits
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from copy import deepcopy


class ClaimService:
    def __init__(self,
                 claim_rep: ClaimRepository = Depends(),
                 user_rep: UserRepository = Depends(),
                 blueprint_rep: BlueprintRepository = Depends(),
                 env_rep: EnvRepository = Depends(),
                 equipment_rep: EquipmentRepository = Depends(),
                 blueprint_service: BlueprintService = Depends(),
                 ):
        self.__claim_repo: ClaimRepository = claim_rep
        self.__user_repo: UserRepository = user_rep
        self.__blueprint_repo: BlueprintRepository = blueprint_rep
        self.__buket_repo: FileBucketRepository = FileBucketRepository("blueprint")
        self.__buket_main_repo: FileBucketRepository = FileBucketRepository("report")
        self.__buket_user_repo: FileBucketRepository = FileBucketRepository("user")
        self.__env_repo: EnvRepository = env_rep
        self.__equipment_repo: EquipmentRepository = equipment_rep
        self.__blueprint_service: BlueprintService = blueprint_service
        self.__count_item: int = 20

    def __get_name_file(self, extend: str) -> str:
        res = ''.join(choice(ascii_letters + digits) for x in range(15))
        return f"{res}.{extend}"

    async def __get_img(self, file_key: str) -> bytes:
        t = await self.__buket_user_repo.get_file(file_key)
        return t

    @property
    def count_item(self) -> int:
        return self.__count_item

    @count_item.setter
    def count_item(self, item):
        self.__count_item = item

    def parse_date(self, date_input: datetime):
        date = date_input

        months = [
            "Январь", "Февраль", "Март", "Апрель",
            "Май", "Июнь", "Июль", "Август",
            "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

        day = date.day
        month_index = date.month - 1  # 0-based
        month_str = months[month_index]
        month_int = str(date.month).zfill(2)
        year = date.year

        return {
            "day": day,
            "month": {
                "str": month_str,
                "int": month_int
            },
            "year": year
        }

    async def get_count_page(self) -> int:
        count_row = await self.__claim_repo.count_row()
        sub_page = 0
        if count_row % self.__count_item > 0:
            sub_page += 1
        return count_row // self.__count_item + sub_page

    async def __get_scheme_template(self, blueprint: Blueprint) -> FileSchemas:
        scheme = await self.__buket_repo.get_file(blueprint.path_map_data_json_file.replace("\\", "/"))
        models = FileSchemas.model_validate_json(scheme)
        return models

    async def get_page(self, num_page: int, user: UserGet) -> list[GetClaim]:
        start = (num_page - 1) * self.__count_item
        if user.type.system_name == "user":
            entities = await self.__claim_repo.get_limit_user(start, self.__count_item)
        else:
            entities = await self.__claim_repo.get_limit_admin(start, self.__count_item)
        claims = [GetClaim.model_validate(entity, from_attributes=True) for entity in entities]
        return claims

    async def update_data_claim(self,
                                uuid_claim: str,
                                schema: str,
                                protocols: str,
                                uuid_user: str,
                                file: UploadFile):
        claim = await self.__claim_repo.get_by_uuid(uuid_claim)
        protocols = protocols.split(",")
        schema = loads(schema)
        schema["list_workers"] = list(schema["list_workers"].values())

        del schema["selectedProtocols"]

        claim.blueprint_json_file = schema

        main_file = await self.__buket_main_repo.get_file(claim.blueprint_xlsx_file.replace("\\", "/"))
        target_file = XlsxFile(None, file.file.read())
        main_file = XlsxFile(None, main_file)

        target_file.read_file(False)
        main_file.read_file(False)

        for i in protocols:
            target_file.copy_sheet(i, main_file)

        buffer = BytesIO()
        main_file.file.save(buffer)
        buffer.seek(0)

        await self.__buket_main_repo.delete_file(claim.blueprint_xlsx_file.replace('\\', '/'))

        await self.__buket_main_repo.upload_file(claim.blueprint_xlsx_file.replace('\\', '/'),
                                                 buffer.getvalue(),
                                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        await self.__claim_repo.add(claim)

    async def generate_file_claim(self, uuid_claim: str):
        claim = await self.__claim_repo.get_by_uuid(uuid_claim)

        schema = deepcopy(claim.blueprint_json_file)
        schema["date"] = self.parse_date(datetime.now())
        schema["claim"] = {
            "name_claim": claim.name
        }
        for i in range(len(schema["list_workers"])):
            schema["list_workers"][i]["painting"] = await self.__get_img(schema["list_workers"][i]["painting"])

        json_map = await self.__get_scheme_template(claim.blueprint)

        main_file = await self.__buket_main_repo.get_file(claim.blueprint_xlsx_file.replace("\\", "/"))

        parser_file_form = ParserFormFile(json_map, XlsxFile(json_map, main_file))
        parser_file_form.parser()

        template = await self.__buket_repo.get_file(claim.blueprint.path_template_docx_file.replace("\\", "/"))

        builder = BuilderDocxFile(template, parser_file_form.map_data)
        builder.build(schema)

        buffer = BytesIO()
        builder.file.save(buffer)
        buffer.seek(0)
        name_file_docx = Path(str(claim.uuid), f"Основной_документ_{claim.name}.docx")

        await self.__buket_main_repo.upload_file(str(name_file_docx).replace('\\', '/'),
                                                 buffer.getvalue(),
                                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        claim.main_document = str(name_file_docx)
        await self.__claim_repo.add(claim)

    async def add_claim(self, data: PostClaim, uuid_user: str):
        blueprint = await self.__blueprint_repo.get_by_uuid(data.uuid_blueprint)
        user = await self.__user_repo.get_user_by_uuid(uuid_user)
        equipment = await self.__equipment_repo.get_by_uuid(data.uuid_equipment)

        state_claim = await self.__env_repo.get_state_claim_by_system_name("draft")
        schema = await self.__blueprint_service.get_file_schemas(blueprint.uuid)

        file_xlsx = await self.__buket_repo.get_file(str(blueprint.path_form_xlsx_file).replace('\\', '/'))
        uuid_claim = uuid4()
        name_file_save = Path(str(uuid_claim), "save_tables_file.xlsx")
        await self.__buket_main_repo.upload_file(str(name_file_save).replace('\\', '/'),
                                                 file_xlsx,
                                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        claim_model = Claim(
            uuid=uuid_claim,
            name=data.name,
            id_state_claim=state_claim.id,
            id_user=user.id,
            id_blueprint=blueprint.id,
            id_equipment=equipment.id,
            blueprint_xlsx_file=str(name_file_save),
            blueprint_json_file=schema.model_dump()
        )
        await self.__claim_repo.add(claim_model)

    async def get(self, uuid: str) -> FullOneClaim:
        claim = await self.__claim_repo.get_by_uuid(uuid)
        return FullOneClaim.model_validate(claim, from_attributes=True)

    async def update(self,
                     uuid: str,
                     main_file: UploadFile | None,
                     edit_file: UploadFile | None,
                     comment: str | None):
        claim = await self.__claim_repo.get_by_uuid(uuid)
        if main_file:
            await self.__buket_main_repo.delete_file(claim.main_document.replace("\\", "/"))
            await self.__buket_main_repo.upload_file(claim.main_document.replace("\\", "/"),
                                                     main_file.file.read(),
                                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        if edit_file:
            name_file = claim.edit_document
            if name_file:
                await self.__buket_main_repo.delete_file(name_file.replace("\\", "/"))
            else:
                name_file = Path(claim.uuid, "Документ_с_пометками.docx")
                claim.edit_document = name_file
            await self.__buket_main_repo.upload_file(str(name_file).replace("\\", "/"),
                                                     edit_file.file.read(),
                                                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        claim.comment = comment
        await self.__claim_repo.add(claim)

    async def update_state_claim(self,
                                 uuid_claim: str,
                                 state_claim: str,
                                 user: UserGet):
        claim = await self.__claim_repo.get_by_uuid(uuid_claim)
        if user.type.system_name == "user":
            if claim.state_claim.system_name in ("draft", "under_development"):
                state_claim_model = await self.__env_repo.get_state_claim_by_system_name("under_consideration")
                claim.id_state_claim = state_claim_model.id
            elif claim.state_claim.system_name == "under_consideration":
                time_delta = datetime.now(timezone.utc) - claim.datetime
                if time_delta.seconds <= 24 * 60 * 60:
                    state_claim_model = await self.__env_repo.get_state_claim_by_system_name("draft")
                    claim.id_state_claim = state_claim_model.id
                else:
                    raise Exception

        else:
            if claim.state_claim.system_name == "under_consideration":
                if state_claim == "accepted":
                    state_claim_model = await self.__env_repo.get_state_claim_by_system_name("accepted")
                else:
                    state_claim_model = await self.__env_repo.get_state_claim_by_system_name("under_development")
                claim.id_state_claim = state_claim_model.id
        await self.__claim_repo.add(claim)

    async def delete_claim(self, uuid: str):
        claim = await self.__claim_repo.get_by_uuid(uuid)
        try:
            if claim.blueprint_xlsx_file:
                await self.__buket_main_repo.delete_file(claim.blueprint_xlsx_file.replace("\\", "/"))
            if claim.edit_document:
                await self.__buket_main_repo.delete_file(claim.edit_document.replace("\\", "/"))
            if claim.main_document:
                await self.__buket_main_repo.delete_file(claim.main_document.replace("\\", "/"))
            await self.__claim_repo.delete(claim)
        except:
            raise Exception
