from fastapi import APIRouter, Depends, status, Response, UploadFile, File, Form
from fastapi.responses import JSONResponse
from ..functions import access_control

from ..services import get_current_user, BlueprintService

from ..models.Blueprint import GetBlueprint
from ..models.Message import Message
from ..models.User import UserGet
from untils.Models.Fileschame import FileSchemas

from typing import Annotated, Optional

router = APIRouter(prefix="/blueprint", tags=["blueprint"])
message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_406_NOT_ACCEPTABLE)
}


@router.get("/page", response_model=list[GetBlueprint],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_page_blueprint(response: Response,
                             page: int = 1,
                             per_item_page: int = 20,
                             current_user: UserGet = Depends(get_current_user),
                             service: BlueprintService = Depends()):
    service.count_item = per_item_page
    count_page = await service.get_count_page()
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(per_item_page)
    blueprints = await service.get_page(page)
    return blueprints


@router.get("/get/file_schemas/{uuid}", response_model=FileSchemas,
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            })
async def get_file_schemas(uuid: str,
                           current_user: UserGet = Depends(get_current_user),
                           service: BlueprintService = Depends()):
    blueprint = await service.get_file_schemas(uuid)
    return blueprint


@router.post("", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["admin", "super_admin"])
async def add_file(file_blueprint: UploadFile,
                   name: Annotated[str, Form()],
                   id_type: Annotated[int, Form()],
                   id_plant: Annotated[int, Form()],
                   current_user: UserGet = Depends(get_current_user),
                   service: BlueprintService = Depends()):
    await service.add_blueprint(name, id_type, id_plant, file_blueprint)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.post("/xlsx_file/{uuid}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_205_RESET_CONTENT: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["admin", "super_admin"])
async def upload_xlsx_file(file: UploadFile,
                           uuid: str,
                           current_user: UserGet = Depends(get_current_user),
                           service: BlueprintService = Depends()):
    await service.upload_xlsx(uuid, file)
    return JSONResponse(content={"message": "Обновлен"},
                        status_code=status.HTTP_205_RESET_CONTENT)


@router.post("/docx_file/{uuid}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_205_RESET_CONTENT: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["admin", "super_admin"])
async def upload_docx_file(file: UploadFile,
                           uuid: str,
                           current_user: UserGet = Depends(get_current_user),
                           service: BlueprintService = Depends()):
    await service.upload_docx(uuid, file)
    return JSONResponse(content={"message": "Обновлен"},
                        status_code=status.HTTP_205_RESET_CONTENT)