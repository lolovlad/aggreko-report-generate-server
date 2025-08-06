from fastapi import APIRouter, Depends, status, Response, UploadFile, File
from fastapi.responses import JSONResponse
from ..functions import access_control

from ..services import get_current_user, DeviceService

from ..models.Device import GetDevice, PostDevice
from ..models.Message import Message
from ..models.User import UserGet

from typing import Annotated, Optional

router = APIRouter(prefix="/device", tags=["device"])
message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_406_NOT_ACCEPTABLE)
}


@router.get("/page", response_model=list[GetDevice],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_page_device(response: Response,
                          page: int = 1,
                          per_item_page: int = 20,
                          current_user: UserGet = Depends(get_current_user),
                          service: DeviceService = Depends()):
    service.count_item = per_item_page
    count_page = await service.get_count_page()
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(per_item_page)
    blueprints = await service.get_page(page)
    return blueprints


@router.post("", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def add_device(data: PostDevice,
                     current_user: UserGet = Depends(get_current_user),
                     service: DeviceService = Depends()):
    await service.create(data)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.get("/search", response_model=list[GetDevice],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_200_OK: {"model": Message}
            })
async def get_device_by_search(search_field: str,
                               service: DeviceService = Depends(),
                               current_user: UserGet = Depends(get_current_user)
                               ):
    device = await service.get_by_search_field(search_field)
    return device


@router.post("/update_file", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["super_admin"])
async def import_type_equip(file: UploadFile = File(...),
                            service: DeviceService = Depends(),
                            current_user: UserGet = Depends(get_current_user)):
    try:
        if file.content_type == "text/csv" or file.content_type == "application/vnd.ms-excel":
            await service.update_date_file(file)
        else:
            return JSONResponse(content={"message": "файл не того типа"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(content={"message": "добавлено"},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        return JSONResponse(content={"message": "ошибка добавления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
