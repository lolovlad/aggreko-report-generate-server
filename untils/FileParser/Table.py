from .Cell import Cell
from ..Models.Fileschame import *


class Table:
    def __init__(self, row_count: int, column_count: int):
        self.__grid: list[list[Cell | None]] = [[None] * column_count for _ in range(row_count)]
        self.__row_count: int = row_count
        self.__column_count: int = column_count

    @property
    def row_count(self):
        return self.__row_count

    @property
    def column_count(self):
        return self.__column_count

    def add_cell(self,
                 x: int,
                 y: int,
                 width: int,
                 height: int,
                 text: str):
        self.__grid[y][x] = Cell(y=y, width=width, x=x, height=height, text=text)

    def edit_text_cell(self, x: int, y: int, new_text: str):
        self.__grid[y][x].text = new_text

    def find_all_data_cell(self) -> list[Cell]:
        list_cells = []
        for row in self.__grid:
            for cell in row:
                if cell is not None:
                    if cell.is_data_cell():
                        list_cells.append(cell)
        return list_cells

    def get_schemas(self) -> TableSchemas:
        list_cells = []
        for row in self.__grid:
            for cell in row:
                if cell is not None:
                    list_cells.append(cell.get_schemas())
        return TableSchemas(
            cells=list_cells
        )

    def __getitem__(self, key):
        return self.__grid[key]
