from fastapi import APIRouter, Depends, status, Response, UploadFile, File, Form
from fastapi.responses import JSONResponse
from ..functions import access_control

from ..services import get_current_user, ClaimService

from ..models.Claim import GetClaim
from ..models.Message import Message
from ..models.User import UserGet
from untils.Models.Fileschame import FileSchemas

from typing import Annotated, Optional


router = APIRouter(prefix="/claim", tags=["claim"])
message_error = {
    status.HTTP_406_NOT_ACCEPTABLE: JSONResponse(content={"message": "отказ в доступе"},
                                                 status_code=status.HTTP_406_NOT_ACCEPTABLE)
}


@router.get("/page", response_model=list[GetClaim],
            responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
            })
async def get_page_claim(response: Response,
                         page: int = 1,
                         per_item_page: int = 20,
                         current_user: UserGet = Depends(get_current_user),
                         service: ClaimService = Depends()):
    service.count_item = per_item_page
    if current_user.type.name == "user":
        count_page = await service.get_count_page(current_user.uuid)
    else:
        count_page = await service.get_count_page(None)
    claims = await service.get_page(page, current_user)

    response.headers["X-Count-Page"] = str(count_page)
    response.headers["X-Count-Item"] = str(per_item_page)

    return claims


@router.post("/{uuid_blueprint}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
@access_control(["user"])
async def create_claim(file_xlsx: UploadFile,
                       schema: Annotated[str, Form()],
                       uuid_blueprint: str,
                       current_user: UserGet = Depends(get_current_user),
                       service: ClaimService = Depends()):
    await service.add_claim(uuid_blueprint, schema, current_user.uuid, file_xlsx)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.get("/get/{uuid}", response_model=GetClaim, responses={
                status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
})
async def get_claim(uuid: str,
                    current_user: UserGet = Depends(get_current_user),
                    service: ClaimService = Depends()):
    claim = await service.get(uuid)
    return claim


@router.post("/update/{uuid}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_201_CREATED: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message}
})
async def update_claim(uuid: str,
                       file_main: Annotated[Optional[UploadFile], File()] = None,
                       file_edit: Annotated[Optional[UploadFile], File()] = None,
                       comment: Annotated[Optional[str], Form()] = None,
                       current_user: UserGet = Depends(get_current_user),
                       service: ClaimService = Depends()):
    await service.update(uuid, file_main, file_edit, comment)
    return JSONResponse(content={"message": "добавлено"},
                        status_code=status.HTTP_201_CREATED)


@router.put("/update/state/{uuid_claim}/{state_claim}", responses={
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Message},
    status.HTTP_200_OK: {"model": Message},
})
async def update_claim_state(uuid_claim: str,
                             state_claim: str,
                             current_user: UserGet = Depends(get_current_user),
                             service: ClaimService = Depends()
                             ):
    try:
        await service.update_state_claim(uuid_claim, state_claim, current_user)
    except Exception:
        return JSONResponse(content={"message": "ошибка обновления состояния"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
