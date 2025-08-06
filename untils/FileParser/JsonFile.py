from pathlib import Path
import json

from ..Models.Fileschame import *


class JsonFile:
    def __init__(self, path_file: Path, file: dict = {}):
        self.__path_file: Path = self.__create_path_to_file(path_file)
        self.__scheme: dict = file

    @property
    def scheme(self):
        return self.__scheme

    def __is_json_file(self, path: Path):
        return path.suffix == ".json"

    def __create_path_to_file(self, path: Path) -> Path:
        if not self.__is_json_file(path):
            path_file = path.parent
            name_file = path.stem
            return Path(path_file, name_file + ".json")
        else:
            return path

    def save_file(self):
        with open(self.__path_file, 'w') as file:
            json.dump(self.__scheme, file, indent=5)

    def read_file(self):
        with open(self.__path_file, 'r') as file:
            data = json.load(file)
            self.__scheme = data

