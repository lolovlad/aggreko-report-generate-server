from .DocxFile import DocxFile
from pathlib import Path
from ..Models.Fileschame import *
from .Table import Table
import json


class ParserTemplateFile:
    def __init__(self, file: bytes, re_end_table: str = "НаименованиеИОиИС"):
        self.__file: DocxFile = DocxFile(file)
        self.__map_data: dict = {}
        self.__skip_top_table: int = 1
        self.__skip_bottom_table: int = 3
        self.__re_end_table: str = re_end_table
        self.__file_schema = FileSchemas()

    @property
    def file_schema(self):
        return self.__file_schema

    @property
    def map_data(self):
        return self.__map_data

    @property
    def file(self):
        return self.__file.file

    def parser(self):
        id_protocol = 0
        tables = self.__file.get_all_parser_table_in_file(r'(?<={{).*?(?=}})')
        tables_in_protocol = []

        system_table = Table(2, 2)
        system_i = 0

        table_workers = None
        table_equipment = None
        table_comment = None

        for id_table, key, table in tables:
            if key == "system_var":
                data_cell = table.find_all_data_cell()
                for i in data_cell:
                    text_data = i.text
                    if text_data == "date":
                        print(id_protocol, system_i)
                        system_table.add_cell(0, system_i, 1, 1, "Дата составления")
                        system_table.add_cell(1, system_i, 1, 1, "{{date}}")
                        system_i += 1
                        self.__file.rename_cell(id_table,
                                                "{{date}}",
                                                "{{protocols[" + str(id_protocol) + "].system_table.date}}")
                    elif text_data == "temp":
                        system_table.add_cell(0, system_i, 1, 1, "Температура (С°)")
                        system_table.add_cell(1, system_i, 1, 1, "{{temp}}")
                        self.__file.rename_cell(id_table,
                                                "{{temp}}",
                                                "{{protocols[" + str(id_protocol) + "].system_table.temp}}")
                        system_i += 1
            elif key == "data_table":
                table = self.__file.generate_key_empty_cell(id_table)
                tables_in_protocol.append(table)
            elif key == "worker_table":
                id_protocol += 1
                protocol = self.__create_protocol(f"{id_protocol}",
                                                  tables_in_protocol,
                                                  system_table,
                                                  )

                tables_in_protocol.clear()
                self.__file_schema.protocols.append(protocol)
                system_table = Table(2, 2)
                system_i = 0

    def __is_end_protocol(self, cell):
        search_str = "".join(cell.text.split())
        return len(cell.text) > 0 and search_str == self.__re_end_table

    def __create_protocol(self, name, tables, system_table) -> Protocol:

        protocol = Protocol(
            name=name,
            tables=[tb.get_schemas() for tb in tables],
            system_table=system_table.get_schemas()
        )
        return protocol
