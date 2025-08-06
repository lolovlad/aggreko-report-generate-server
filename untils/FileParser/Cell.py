from re import findall
from ..Models.Fileschame import CellSchemas, Size


class Cell:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.__x: int = x + 1
        self.__y: int = y + 1
        self.__width: int = width
        self.__height: int = height
        self.__text: str = text
        self.__re: str = r'(?<={{).*?(?=}})'

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def text(self):
        text = self.__get_text(self.__text)
        return text if text is not None else self.__text

    @text.setter
    def text(self, new_: str):
        self.__text = new_

    def is_merge_cell(self) -> bool:
        return self.__width > 1 or self.__height > 1

    def is_data_cell(self) -> bool:
        return self.__get_text(self.__text) is not None

    def __get_text(self, text) -> str | None:
        text_re = findall(self.__re, text)
        return text_re[0] if len(text_re) > 0 else None

    def get_schemas(self) -> CellSchemas:
        return CellSchemas(
            x=self.x,
            y=self.y,
            is_merge=self.is_merge_cell(),
            is_data=self.is_data_cell(),
            text=self.text,
            size=Size(
                width=self.width,
                height=self.height
            )
        )

    def __repr__(self):
        return f"{self.__text} coord: x-{self.__x} y-{self.__y}"