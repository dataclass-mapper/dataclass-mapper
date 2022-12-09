from abc import ABC, abstractmethod

from ..fieldmeta import FieldMeta


class Assignment(ABC):
    def __init__(self, source: FieldMeta, target: FieldMeta):
        """
        :param source: meta infos about the source field
        :param target: meta infos about the target field
        """
        self.source = source
        self.target = target

    @abstractmethod
    def applicable(self) -> bool:
        ...

    @abstractmethod
    def right_side(self) -> str:
        ...
