from abc import ABC, abstractmethod
from typing import TypeVar, Type

SourceParserType = TypeVar("SourceParserType", bound="SourceParser")

class SourceParser(ABC):
    def __init__(self, content: str) -> None:
        self.content = content

    @classmethod
    def load_file(cls: Type[SourceParserType], path: str) -> SourceParserType:
        with open(path, "r", encoding="utf-8") as file:
            file_content = file.read()

        return cls(file_content)

__all__ = ["SourceParser"]