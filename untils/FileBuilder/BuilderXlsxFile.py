from .BuilderFile import BuilderFile

from ..FileParser.XlsxFile import XlsxFile
from ..FileParser.JsonFile import JsonFile

from ..Models.Fileschame import *

from copy import deepcopy
from pathlib import Path
from re import findall


class BuilderXlsxFile(BuilderFile):
    def __init__(self, path_file: Path, file_schemas: FileSchemas):
        self.__file: XlsxFile = XlsxFile(file_schemas)
        self.__schemas: FileSchemas = file_schemas
        self.__json_data_schema: dict = {}
        self.__path_file: Path = path_file

    @property
    def file_xlsx(self):
        return self.__file.file

    @property
    def schemas(self):
        return self.__schemas

    def build(self):
        for id_protocol, target_protocol in enumerate(self.__schemas.protocols):
            self.__file.create_sheet(target_protocol)

            bias = 5
            last_y_cell = 0

            self.__json_data_schema[target_protocol.name] = {}
            new_cells = []
            for id_cell, cell in enumerate(target_protocol.system_table.cells):
                x = cell.x
                y = cell.y + bias + last_y_cell
                if cell.is_data:
                    self.__create_data_cell(x, y, cell)
                    cell.global_x = x
                    cell.global_y = y
                    cell.text = self.__file.get_text_in_cell(cell.text)
                    new_cells.append(cell)
                else:
                    self.__file.create_cell(x, y, cell.text)
            self.__schemas.protocols[id_protocol].system_table.cells = new_cells
            last_y_cell = y - 2

            for id_table, table in enumerate(target_protocol.tables):
                new_cells = []
                for id_cell, cell in enumerate(table.cells):

                    x = cell.x
                    y = cell.y + bias + last_y_cell

                    if cell.is_data:
                        self.__create_data_cell(x, y, cell)

                        cell.global_x = x
                        cell.global_y = y
                        cell.text = self.__file.get_text_in_cell(cell.text)

                        new_cells.append(cell)
                    elif cell.is_merge:
                        self.__create_merge_cell(x, y, cell.size, cell.text)
                    else:
                        self.__file.create_cell(x, y, cell.text)
                self.add_to_table(id_protocol, id_table, new_cells)
                last_y_cell = y - 2

    def add_to_table(self, id_protocol: int, id_table: int, new_cells: list):
        self.__schemas.protocols[id_protocol].tables[id_table].cells = new_cells

    def __get_json_data_schema(self, sheet, key):
        return self.__json_data_schema[sheet][key]

    def __is_cell_ref(self, text: str):
        coord = self.__json_data_schema[self.__file.get_title_sheet()].get(text)
        return coord is not None

    def __create_data_cell(self, x: int, y: int, cell: CellSchemas):
        text = self.__file.get_text_in_cell(cell.text)
        if self.__is_cell_ref(text):
            coord_ref_cell = self.__get_json_data_schema(self.__file.get_title_sheet(), text)
            text = self.__create_ref_to_cell(coord_ref_cell[0], coord_ref_cell[1])
        else:
            self.__add_to_schema(x, y, text)
            self.__file.add_fill_cell(x, y)
            text = ""
        if cell.is_merge:
            self.__create_merge_cell(x, y, cell.size, text)
        self.__file.create_cell(x, y, text)

    def __create_merge_cell(self, x: int, y: int, size: Size, text: str):
        try:
            self.__file.create_cell(x, y, text)

            end_x = x + size.width - 1
            end_y = y + size.height - 1

            self.__file.merge_cells(x, y, end_x, end_y)
        except AttributeError:
            pass

    def __add_to_schema(self, x: int, y: int, text: str):
        title_sheet = self.__file.get_title_sheet()
        self.__json_data_schema[title_sheet][self.__file.get_text_in_cell(text)] = (x, y)

    def __create_ref_to_cell(self, x: int, y: int) -> str:
        coord_cell = self.__file.get_coord_cell(x, y)
        return f"={coord_cell}"
