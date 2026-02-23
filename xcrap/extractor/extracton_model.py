from abc import ABC, abstractmethod

class ExtractionModel(ABC):
    @abstractmethod
    def extract(self, content: str) -> any:
        pass