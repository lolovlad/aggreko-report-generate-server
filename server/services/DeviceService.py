from fastapi import Depends,  UploadFile

from ..repositories import DeviceRepository
from ..models.Device import *
from ..tables import Device

from io import StringIO
import csv

class DeviceService:
    def __init__(self,
                 device_rep: DeviceRepository = Depends()):
        self.__device_repo: DeviceRepository = device_rep
        self.__count_item: int = 20

    @property
    def count_item(self) -> int:
        return self.__count_item

    @count_item.setter
    def count_item(self, item):
        self.__count_item = item

    async def get_count_page(self) -> int:
        count_row = await self.__device_repo.count_row()
        sub_page = 0
        if count_row % self.__count_item > 0:
            sub_page += 1
        return count_row // self.__count_item + sub_page

    async def get_page(self, num_page: int) -> list[GetDevice]:
        start = (num_page - 1) * self.__count_item
        entities = await self.__device_repo.get_limit(start, self.__count_item)
        devices = [GetDevice.model_validate(entity, from_attributes=True) for entity in entities]
        return devices

    async def create(self, data: PostDevice):
        entity = Device(
            name=data.name,
            id_type=data.id_type,
            error=data.error,
            code=data.code,
            date_check_last=data.date_check_last.replace(tzinfo=None),
            date_check_next=data.date_check_next.replace(tzinfo=None)
        )
        try:
            await self.__device_repo.add(entity)
        except Exception:
            raise Exception

    async def get_by_id(self, id_device: int) -> GetDevice | None:
        device = await self.__device_repo.get_device_by_id(id_device)
        if device is None:
            return None
        return GetDevice.model_validate(device, from_attributes=True)

    async def get_by_search_field(self, search_field: str) -> list[GetDevice]:
        entities = await self.__device_repo.get_device_by_search_field(search_field)
        device = [GetDevice.model_validate(entity, from_attributes=True) for entity in entities]
        return device

    async def update_date_file(self, file: UploadFile):
        try:
            while contents := await file.read(1024 * 1024):
                buffer = StringIO(contents.decode('utf-8-sig'))
                csv_reader = csv.DictReader(buffer, delimiter=';')

                for rows in csv_reader:
                    devices = await self.__device_repo.get_device_by_code(rows["Заводской номер"])
                    if len(devices) == 1:
                        try:
                            date_start = datetime.strptime(rows["Дата поверки"], '%d.%m.%Y')
                            date_end = datetime.strptime(rows["Дата следующей поверки"], '%d.%m.%Y')
                        except Exception:
                            date_start = datetime.min
                            date_end = datetime.max
                        devices[0].date_check_last = date_start
                        devices[0].date_check_next = date_end
                        await self.__device_repo.update(devices[0])

        except Exception:
            raise Exception()
        finally:
            await file.close()
