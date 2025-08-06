from abc import ABC, abstractmethod
from pathlib import Path


class File(ABC):

    @abstractmethod
    def render(self, schemas: dict):
        pass

    @abstractmethod
    def is_table_schema(self, table, re: str):
        pass

    @abstractmethod
    def get_all_parser_table_in_file(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_list_cells(self,  table):
        pass