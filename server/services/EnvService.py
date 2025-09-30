from fastapi import Depends, UploadFile

from ..models.Mixins import SystemVariablesMixin
from ..models.User import GetTypeUser, Profession
from ..models.Blueprint import TypeBlueprintModel, TypeEquipmentBlueprintModel
from ..models.Device import TypeDeviceModel
from ..models.Equipment import TypeEquipmentModel

from ..tables import (Profession as ProfessionORM,
                      TypeEquipment,
                      TypeEquipmentBlueprint,
                      TypeBlueprint,
                      TypeDevice)

from ..repositories import EnvRepository

from io import StringIO
import csv


class EnvService:
    def __init__(self,
                 env_repo: EnvRepository = Depends()):
        self.__env_repo: EnvRepository = env_repo

    async def get_type_users(self) -> list[GetTypeUser]:
        type_users = await self.__env_repo.get_all_type_user()
        return [GetTypeUser.model_validate(obj, from_attributes=True) for obj in type_users]

    async def add_profession(self, prof: Profession):
        entity = ProfessionORM()
        data = prof.model_dump()
        for i in data:
            if i != "id":
                setattr(entity, i, data[i])
        prof = await self.__env_repo.add(entity)

    async def get_profession_user(self) -> list[Profession]:
        prof_users = await self.__env_repo.get_all_prof_user()
        return [Profession.model_validate(obj, from_attributes=True) for obj in prof_users]

    async def delete_prof(self, id_prof: int) -> bool:
        try:
            prof = await self.__env_repo.get_entity(id_prof, ProfessionORM)
            prof.is_delite = True
            await self.__env_repo.add(prof)
            return True
        except:
            return False

    async def get_type_blueprint(self) -> list[TypeBlueprintModel]:
        type_blueprint = await self.__env_repo.get_all_type_blueprint()
        return [TypeBlueprintModel.model_validate(i, from_attributes=True) for i in type_blueprint]

    async def get_type_equipment_blueprint(self) -> list[TypeEquipmentBlueprintModel]:
        type_equipment_blueprint = await self.__env_repo.get_all_type_equipment_blueprint()
        return [TypeEquipmentBlueprintModel.model_validate(i, from_attributes=True) for i in type_equipment_blueprint]

    async def get_type_device(self) -> list[TypeDeviceModel]:
        type_device = await self.__env_repo.get_all_type_device()
        return [TypeDeviceModel.model_validate(i, from_attributes=True) for i in type_device]

    async def add_type_blueprint(self, data: SystemVariablesMixin):
        entity = TypeBlueprint()
        data = data.model_dump()
        for i in data:
            if i != "id":
                setattr(entity, i, data[i])
        await self.__env_repo.add(entity)

    async def add_type_equipment_blueprint(self, data: SystemVariablesMixin):
        entity = TypeEquipmentBlueprint()
        data = data.model_dump()
        for i in data:
            if i != "id":
                setattr(entity, i, data[i])
        await self.__env_repo.add(entity)

    async def add_type_device(self, data: SystemVariablesMixin):
        entity = TypeDevice()
        data = data.model_dump()
        for i in data:
            if i != "id":
                setattr(entity, i, data[i])
        await self.__env_repo.add(entity)

    async def add_type_equipment(self, type_equipment: TypeEquipmentModel) -> ProfessionORM:
        entity = TypeEquipment(
            system_name=type_equipment.system_name,
            name=type_equipment.name,
            code=type_equipment.code,
            description=type_equipment.description)
        type_equipment = await self.__env_repo.add(entity)
        return type_equipment

    async def get_all_type_equip(self) -> list[TypeEquipmentModel]:
        entity = await self.__env_repo.get_all_type_equip()
        return [TypeEquipmentModel.model_validate(i, from_attributes=True) for i in entity]

    async def import_type_equip_file(self, file: UploadFile):
        try:
            type_equipments = []
            while contents := await file.read(1024 * 1024):
                buffer = StringIO(contents.decode('utf-8-sig'))
                csv_reader = csv.DictReader(buffer, delimiter=';')

                for rows in csv_reader:

                    type_equipment = TypeEquipment(
                        system_name=rows["name"],
                        code=rows["code"],
                        name=rows["name"],
                    )
                    type_equipments.append(type_equipment)

                await self.__env_repo.add_list_type_equipment(type_equipments)

        except Exception:
            raise Exception()
        finally:
            await file.close()

    async def delete_type_blueprint(self, id_type_b: int) -> TypeBlueprint:
        entity = await self.__env_repo.get_entity(id_type_b, TypeBlueprint)
        entity.is_delite = True
        await self.__env_repo.add(entity)
        return entity

    async def delete_type_equipment_blueprint(self, id_type_equip_b: int) -> TypeEquipmentBlueprint:
        entity = await self.__env_repo.get_entity(id_type_equip_b, TypeEquipmentBlueprint)
        entity.is_delite = True
        await self.__env_repo.add(entity)
        return entity
