from abc import ABC, abstractmethod


class BuilderFile(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def build(self, *args, **kwargs):
        pass