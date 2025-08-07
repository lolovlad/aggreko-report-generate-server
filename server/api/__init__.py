from fastapi import APIRouter
from .user import router as user_router
from .login import router as login_router
from .env import router as env_router
from .blueprint import router as blueprint_router
from .device import router as device_router
from .claim import router as claim_router
from .equipment import router as equipment_router
from .file import router as file_router


router = APIRouter(prefix="/v1")
router.include_router(user_router)
router.include_router(login_router)
router.include_router(env_router)
router.include_router(blueprint_router)
router.include_router(device_router)
router.include_router(claim_router)
router.include_router(equipment_router)
router.include_router(file_router)




