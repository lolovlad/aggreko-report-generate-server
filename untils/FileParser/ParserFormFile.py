from .XlsxFile import XlsxFile
from pathlib import Path
from ..Models.Fileschame import *


class ParserFormFile:
    def __init__(self, file_schema: FileSchemas, file: XlsxFile):
        self.__file: XlsxFile = file
        self.__file_schema: FileSchemas = file_schema
        self.__map_data: dict = {}

    @property
    def map_data(self) -> dict:
        return self.__map_data

    def parser(self):
        self.__file.read_file(False)
        for name_sheet, target_protocol in zip(self.__file.get_list_sheet(), self.__file_schema.protocols):
            keys_value = {}
            system_table = {}

            self.__file.target_sheet_by_name(name_sheet)

            for table in target_protocol.tables:
                for cell in table.cells:
                    if keys_value.get(cell.text) is None:
                        keys_value[cell.text] = self.__file.get_cell_value(cell.global_x, cell.global_y)
            self.__map_data[target_protocol.name] = keys_value
            for cell in target_protocol.system_table.cells:
                if system_table.get(cell.text) is None:
                    system_table[cell.text] = self.__file.get_cell_value(cell.global_x, cell.global_y)
            self.__map_data[target_protocol.name]["system_table"] = system_table
