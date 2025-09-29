from docxtpl import DocxTemplate, InlineImage
from .BuilderFile import BuilderFile

from pathlib import Path
from io import BytesIO


class BuilderDocxFile(BuilderFile):
    def __init__(self, content: bytes, map_data: dict):
        buffer: BytesIO = BytesIO(content)
        self.__template_path_file = DocxTemplate(buffer)
        self.__map_data: dict = map_data

    @property
    def file(self):
        return self.__template_path_file

    def build(self, map_data_dop: dict):
        self.merge_map_dict()
        self.merge_to_top_map_data(map_data_dop)
        self.__template_path_file.render(self.__map_data)

    def merge_map_dict(self):
        new_map_data = {}
        new_map_data["protocols"] = []
        for name_protocol in self.__map_data:
            for val in self.__map_data[name_protocol]:
                if val != "system_table":
                    new_map_data[val] = self.__map_data[name_protocol][val]
                else:
                    try:
                        self.__map_data[name_protocol][val]["date"] = self.__map_data[name_protocol][val]["date"].strftime("%d.%m.%Y")
                    except:
                        pass
                    new_map_data["protocols"].append(self.__map_data[name_protocol][val])
        self.__map_data = new_map_data

    def merge_to_top_map_data(self, map_data_dop: dict):
        for i in range(len(map_data_dop["list_workers"])):
            image_bytes = map_data_dop["list_workers"][i]["painting"]
            image_stream = BytesIO(image_bytes)
            map_data_dop["list_workers"][i]["painting"] = InlineImage(self.__template_path_file, image_stream)

        for i in range(len(map_data_dop["protocols"])):
            map_data_dop["protocols"][i]["system_table"] = self.__map_data["protocols"][i]
            try:
                map_data_dop["protocols"][i]["list_equipment"] = list(map_data_dop["protocols"][i]["list_equipment"].values())
            except:
                pass
        for key in map_data_dop:
            self.__map_data[key] = map_data_dop[key]

