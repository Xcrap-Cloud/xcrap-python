import json
from typing import Any, Dict, Optional, Type, Union

import jmespath
from pydantic import BaseModel

from .extraction_model import ExtractionModel
from .query_builders import QueryConfig


class JsonBaseField(BaseModel):
    query: QueryConfig
    default: Optional[Any] = None
    multiple: bool = False
    limit: Optional[int] = None


class JsonNestedField(BaseModel):
    query: Optional[QueryConfig] = None
    model: Union[ExtractionModel, Type[ExtractionModel]]
    limit: Optional[int] = None
    default: Optional[Any] = None
    multiple: bool = False

    model_config = {"arbitrary_types_allowed": True}


JsonExtractionField = Union[JsonBaseField, JsonNestedField]


class JsonExtractionModel(ExtractionModel):
    _fields: Dict[str, JsonExtractionField] = {}

    def __init__(self, shape: Optional[Dict[str, JsonExtractionField]] = None) -> None:
        self.shape = shape if shape is not None else self._fields

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        fields = {}

        for name, attr in cls.__dict__.items():
            if isinstance(attr, (JsonBaseField, JsonNestedField)):
                fields[name] = attr

        combined_fields = {}

        for base in reversed(cls.__mro__):
            if hasattr(base, "_fields"):
                combined_fields.update(base._fields)

        combined_fields.update(fields)

        cls._fields = combined_fields

    def extract(self, content: str | dict | list) -> Dict[str, Any]:
        root = content if isinstance(content, (dict, list)) else json.loads(content)

        data: Dict[str, Any] = {}

        for key, value in self.shape.items():
            if isinstance(value, JsonNestedField):
                data[key] = self._extract_nested_value(value, root)

            else:
                data[key] = self._extract_base_value(value, root)

        return data

    def _extract_base_value(self, value: JsonBaseField, root: Any) -> Any:
        result = jmespath.search(value.query["value"], root)

        if result is None:
            return value.default

        if value.multiple:
            if not isinstance(result, list):
                result = [result]

            if value.limit is not None:
                result = result[: value.limit]

            return result if result else (value.default if value.default is not None else [])

        return result

    def _extract_nested_value(self, value: JsonNestedField, root: Any) -> Any:
        extracted_data = jmespath.search(value.query["value"], root) if value.query else root

        if extracted_data is None:
            return value.default

        model = value.model

        if isinstance(model, type):
            model = model()

        if value.multiple:
            if not isinstance(extracted_data, list):
                extracted_data = [extracted_data]

            if value.limit is not None:
                extracted_data = extracted_data[: value.limit]

            results = []

            for item in extracted_data:
                results.append(model.extract(item))

            return results if results else (value.default if value.default is not None else [])

        else:
            return model.extract(extracted_data)
