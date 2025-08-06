from pathlib import Path
from .File import File
from ..Models.Fileschame import *

from re import findall


class FileParser:
    def __init__(self, file: File, file_schema: FileSchemas = FileSchemas()):
        self.__file_schema: FileSchemas = file_schema
        self.__file: File = file

    @property
    def file_schema(self) -> FileSchemas:
        return self.__file_schema

    def parser_data(self):
        id_protocol = 1
        tables = self.__file.get_all_parser_table_in_file(r'{{\w+}}')
        print(tables)
        '''table_schema = []
        for table in tables:
            cell_table = table.cell(0, 0)

            search_str = "".join(cell_table.text.split())

            if len(cell_table.text) > 0 and search_str == "НаименованиеИОиИС":
                protocol = Protocol(name=f"{id_protocol}")
                for tablesc in self.__file.get_list_tables_parser(table_schema, r'{{\w+}}'):
                    protocol.tables.append(TableSchemas(
                        cells=self.__export_table_to_list_cells(tablesc, r'{{\w+}}'))
                    )
                self.__file_schema.protocols.append(protocol)
                id_protocol += 1
                table_schema.clear()
            else:
                table_schema.append(table)'''

    def __export_table_to_list_cells(self, table, re: str) -> list:
        list_cells = self.__file.get_list_cells(table)
        list_cells_schema = []
        for cell in list_cells:
            is_merge = self.__is_merge_cell(cell)
            is_data = self.__is_data_cell(cell, re)
            list_cells_schema.append(CellSchemas(
                x=cell[1],
                y=cell[2],
                is_merge=is_merge,
                is_data=is_data,
                text=cell[0],
                size=Size(
                    width=cell[-1][1],
                    height=cell[-1][0]
                )
            ))
        return list_cells_schema

    def __is_merge_cell(self, cell: list) -> bool:
        size = cell[-1]
        return size[0] > 1 or size[1] > 1

    def __is_data_cell(self, cell: list, re: str) -> bool:
        text = cell[0]
        return len(findall(re, text)) > 0