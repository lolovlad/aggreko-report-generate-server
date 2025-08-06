from fastapi import APIRouter, Depends, status, Request, Response, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse

from ..services import EnvService, get_current_user
from ..models.User import GetTypeUser, Profession


from ..models.Mixins import SystemVariablesMixin
from ..models.Message import Message
from ..models.User import UserGet
from ..models.Blueprint import TypeBlueprintModel, TypeEquipmentBlueprintModel
from ..models.Device import TypeDeviceModel
from ..models.Equipment import TypeEquipmentModel


#from ..models.Object import StateObject, Region, PostRegion
#from ..models.Accident import SignsAccident, GetTypeBrake
#from ..models.Event import StateEvent, TypeEvent
#from ..models.Claim import StateClaimModel

from ..repositories import FileBucketRepository
from ..functions import access_control


router = APIRouter(prefix="/env", tags=["env"])


message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
}


@router.get("/type_user", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[GetTypeUser])
async def get_type_user(service: EnvService = Depends(),
                        current_user: UserGet = Depends(get_current_user)):
    type_users = await service.get_type_users()
    return type_users


@router.get("/profession", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[Profession])
async def get_user_profession(service: EnvService = Depends(),
                              current_user: UserGet = Depends(get_current_user)):
    prof_users = await service.get_profession_user()
    return prof_users


@router.post("/profession", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["super_admin"])
async def add_profession(prof: Profession,
                         service: EnvService = Depends(),
                         current_user: UserGet = Depends(get_current_user)):
    prof_users = await service.add_profession(prof.name, prof.description)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.delete("/profession/{id_prof}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["super_admin"])
async def delete_profession(id_prof: int,
                            service: EnvService = Depends(),
                            current_user: UserGet = Depends(get_current_user)):
    prof = await service.delete_prof(id_prof)
    if prof:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Удалено"})
    else:
        return JSONResponse(content={"message": "ошибка удаление"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/type_blueprint", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[TypeBlueprintModel])
async def get_type_blueprint(service: EnvService = Depends(),
                             current_user: UserGet = Depends(get_current_user)):
    type_blueprints = await service.get_type_blueprint()
    return type_blueprints


@router.post("/type_blueprint", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["super_admin"])
async def add_type_blueprint(data: SystemVariablesMixin,
                             service: EnvService = Depends(),
                             current_user: UserGet = Depends(get_current_user)):
    await service.add_type_blueprint(data)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.get("/type_equipment_blueprint", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[TypeEquipmentBlueprintModel])
async def get_equipment_type_blueprint(service: EnvService = Depends(),
                                       current_user: UserGet = Depends(get_current_user)):
    type_equipment_blueprints = await service.get_type_equipment_blueprint()
    return type_equipment_blueprints


@router.post("/type_equipment_blueprint", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["super_admin"])
async def add_type_equipment_blueprint(data: SystemVariablesMixin,
                                       service: EnvService = Depends(),
                                       current_user: UserGet = Depends(get_current_user)):
    await service.add_type_equipment_blueprint(data)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.get("/type_device", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
}, response_model=list[TypeDeviceModel])
async def get_type_device(service: EnvService = Depends(),
                          current_user: UserGet = Depends(get_current_user)):
    entity = await service.get_type_device()
    return entity


@router.post("/type_device", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["super_admin"])
async def add_type_device(data: SystemVariablesMixin,
                          service: EnvService = Depends(),
                          current_user: UserGet = Depends(get_current_user)):
    await service.add_type_device(data)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.get("/type_equip", response_model=list[TypeEquipmentModel], responses={
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
})
async def get_type_equipment(service: EnvService = Depends()):
    state = await service.get_all_type_equip()
    return state


@router.post("/type_equip", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["super_admin"])
async def add_type_equipment(type_equipment: TypeEquipmentModel,
                             service: EnvService = Depends(),
                             current_user: UserGet = Depends(get_current_user)):
    type_equipment = await service.add_type_equipment(type_equipment)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.post("/type_equip/import_file", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["super_admin"])
async def import_type_equip(file: UploadFile = File(...),
                            service: EnvService = Depends(),
                            current_user: UserGet = Depends(get_current_user)):
    try:
        if file.content_type == "text/csv" or file.content_type == "application/vnd.ms-excel":
            await service.import_type_equip_file(file)
        else:
            return JSONResponse(content={"message": "файл не того типа"},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(content={"message": "добавлено"},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        return JSONResponse(content={"message": "ошибка добавления"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)