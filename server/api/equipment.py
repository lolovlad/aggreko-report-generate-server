from fastapi import APIRouter, Depends, status, Request, Response, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from ..functions import access_control

from ..services import EquipmentService, get_current_user

from ..models.Equipment import *
from ..models.Message import Message


router = APIRouter(prefix="/equipment", tags=["equipment"])


message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
}


@router.get("/page", response_model=list[GetEquipment],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            })
async def get_page_equipment(
        response: Response,
        page: int = 1,
        per_item_page: int = 20,
        current_user: UserGet = Depends(get_current_user),
        service: EquipmentService = Depends()):
    service.count_item = per_item_page
    count_page = await service.get_count_page()
    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(service.count_item)
    t = await service.get_page_equip(page)
    return t


@router.get("/search",
            response_model=list[GetEquipment],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            })
async def search_equipment(
        search_field: str,
        service: EquipmentService = Depends(),
        current_user: UserGet = Depends(get_current_user)
):
    equipment = await service.get_equipment_by_search_field(search_field)
    return equipment


@router.get("/list", response_model=list[GetEquipment],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            })
async def get_all_equipment(
        current_user: UserGet = Depends(get_current_user),
        service: EquipmentService = Depends()):
    return await service.get_all_equip()


@router.get("/get/{uuid}", response_model=GetEquipment,
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
                status.HTTP_404_NOT_FOUND: {"model": Message}
            })
async def get_one_equipment(uuid: str,
                            service: EquipmentService = Depends(),
                            current_user: UserGet = Depends(get_current_user)
):
    obj = await service.get_one(uuid)
    if obj is not None:
        return obj
    else:
        return JSONResponse(content={"message": " не существует"},
                            status_code=status.HTTP_404_NOT_FOUND)


@router.post("", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def add_equipment(
        equipment_target: PostEquipment,
        service: EquipmentService = Depends(),
        current_user: UserGet = Depends(get_current_user)):
    try:
        await service.create_equip(equipment_target)
        return JSONResponse(content={"message": "добавлено"},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        return JSONResponse(content={"message": "ошибка добавления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/{uuid_equipment}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
    status.HTTP_200_OK: {"model": Message},
})
async def delete_equipment(
        uuid_equipment: str,
        service: EquipmentService = Depends(),
        current_user: UserGet = Depends(get_current_user)):
    try:
        await service.delete_equip(uuid_equipment)
        return JSONResponse(content={"message": "Удалено"},
                            status_code=status.HTTP_200_OK)
    except Exception:
        return JSONResponse(content={"message": "ошибка удаления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put("/{uuid_equipment}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
})
async def update_equipment(uuid_equipment: str,
                           target_equipment: UpdateEquipment,
                           service: EquipmentService = Depends(),
                           current_user: UserGet = Depends(get_current_user)):
    try:
        await service.update_equip(uuid_equipment, target_equipment)
        return JSONResponse(content={"message": "Обновленно"},
                            status_code=status.HTTP_200_OK)
    except Exception:
        return JSONResponse(content={"message": "ошибка обновления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
