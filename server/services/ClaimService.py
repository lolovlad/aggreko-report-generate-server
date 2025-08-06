from fastapi import Depends, UploadFile

from ..repositories import ClaimRepository, UserRepository, BlueprintRepository, FileBucketRepository, EnvRepository
from ..models.Claim import *
from ..tables import Claim, Blueprint

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


class ClaimService:
    def __init__(self,
                 claim_rep: ClaimRepository = Depends(),
                 user_rep: UserRepository = Depends(),
                 blueprint_rep: BlueprintRepository = Depends(),
                 env_rep: EnvRepository = Depends()
                 ):
        self.__claim_repo: ClaimRepository = claim_rep
        self.__user_repo: UserRepository = user_rep
        self.__blueprint_repo: BlueprintRepository = blueprint_rep
        self.__buket_repo: FileBucketRepository = FileBucketRepository("blueprint")
        self.__buket_main_repo: FileBucketRepository = FileBucketRepository("report")
        self.__buket_user_repo: FileBucketRepository = FileBucketRepository("user")
        self.__env_repo: EnvRepository = env_rep
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

    async def get_count_page(self, uuid_user: str | None) -> int:
        id_user = None
        if uuid_user:
            user = await self.__user_repo.get_user_by_uuid(uuid_user)
            id_user = user.id

        count_row = await self.__claim_repo.count_row(id_user)
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
            user = await self.__user_repo.get_user_by_uuid(user.uuid)
            entities = await self.__claim_repo.get_limit_user(user.id, start, self.__count_item)
        else:
            entities = await self.__claim_repo.get_limit_admin(start, self.__count_item)
        claims = [GetClaim.model_validate(entity, from_attributes=True) for entity in entities]
        return claims

    async def add_claim(self,
                        uuid_blueprint: str,
                        schema: str,
                        uuid_user: str,
                        file: UploadFile):
        blueprint = await self.__blueprint_repo.get_by_uuid(uuid_blueprint)
        user = await self.__user_repo.get_user_by_uuid(uuid_user)

        schema = loads(schema)
        uuid_claim = uuid4()
        schema["list_workers"] = list(schema["list_workers"].values())
        for i in range(len(schema["list_workers"])):
            schema["list_workers"][i]["painting"] = await self.__get_img(schema["list_workers"][i]["painting"])

        json_map = await self.__get_scheme_template(blueprint)

        parser_file_form = ParserFormFile(json_map, XlsxFile(json_map, file.file.read()))
        parser_file_form.parser()

        template = await self.__buket_repo.get_file(blueprint.path_template_docx_file.replace("\\", "/"))

        builder = BuilderDocxFile(template, parser_file_form.map_data)
        builder.build(schema)

        buffer = BytesIO()
        builder.file.save(buffer)
        buffer.seek(0)
        name_file_docx = Path(str(uuid_claim), "Основной_документ.docx")

        await self.__buket_main_repo.upload_file(str(name_file_docx).replace('\\', '/'),
                                                 buffer.getvalue(),
                                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        state_claim = await self.__env_repo.get_state_claim_by_system_name("draft")

        claim_model = Claim(
            uuid=uuid_claim,
            datetime=datetime.now().replace(tzinfo=None),
            id_state_claim=state_claim.id,
            id_user=user.id,
            id_blueprint=blueprint.id,
            main_document=str(name_file_docx),
        )

        await self.__claim_repo.add(claim_model)

    async def get(self, uuid: str) -> GetClaim:
        claim = await self.__claim_repo.get_by_uuid(uuid)
        return GetClaim.model_validate(claim, from_attributes=True)

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