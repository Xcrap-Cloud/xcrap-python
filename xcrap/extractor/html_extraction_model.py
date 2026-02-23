from typing import Any, Dict, Optional, Union, Type
from pydantic import BaseModel
from parsel import Selector

from .extracton_model import ExtractionModel
from .query_builders import QueryConfig


class HtmlBaseField(BaseModel):
    query: QueryConfig
    default: Optional[Any] = None
    multiple: bool = False
    limit: Optional[int] = None


class HtmlNestedField(BaseModel):
    query: Optional[QueryConfig] = None
    model: Union[ExtractionModel, Type[ExtractionModel]]
    limit: Optional[int] = None
    default: Optional[Any] = None
    multiple: bool = False

    model_config = {"arbitrary_types_allowed": True}


HtmlExtractionField = Union[HtmlBaseField, HtmlNestedField]


class HtmlExtractionModel(ExtractionModel):
    _fields: Dict[str, HtmlExtractionField] = {}

    def __init__(self, shape: Optional[Dict[str, HtmlExtractionField]] = None) -> None:
        self.shape = shape if shape is not None else self._fields

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        fields = {}

        for name, attr in cls.__dict__.items():
            if isinstance(attr, (HtmlBaseField, HtmlNestedField)):
                fields[name] = attr

        combined_fields = {}

        for base in reversed(cls.__mro__):
            if hasattr(base, "_fields"):
                combined_fields.update(base._fields)

        combined_fields.update(fields)

        cls._fields = combined_fields

    def extract(self, content: str | Selector) -> Dict[str, Any]:
        root = content if isinstance(content, Selector) else Selector(text=content)

        data: Dict[str, Any] = {}

        for key, value in self.shape.items():
            if isinstance(value, HtmlNestedField):
                data[key] = self._extract_nested_value(value, root)

            else:
                data[key] = self._extract_base_value(value, root)

        return data

    def _extract_base_value(self, value: HtmlBaseField, root: Selector) -> Any:
        elements = self._select_elements(value.query, root)

        if value.multiple:
            if value.limit is not None:
                elements = elements[: value.limit]

            results = elements.getall()
            return (
                results
                if results
                else (value.default if value.default is not None else [])
            )
        else:
            result = elements.get()
            if result is None:
                return value.default
            return result

    def _extract_nested_value(self, value: HtmlNestedField, root: Selector) -> Any:
        elements = self._select_elements(value.query, root) if value.query else [root]

        model = value.model

        if isinstance(model, type):
            model = model()

        if value.multiple:
            if value.query is None:
                raise Exception(
                    "Query is required for nested model with multiple values"
                )

            if value.limit is not None:
                elements = elements[: value.limit]

            results = []

            for el in elements:
                results.append(model.extract(el))

            return (
                results
                if results
                else (value.default if value.default is not None else [])
            )

        else:
            element = elements[0] if len(elements) > 0 else None

            if element is None:
                return value.default

            return model.extract(element)

    def _select_elements(self, query: QueryConfig, root: Selector):
        if query["type"] == "css":
            return root.css(query["value"])

        return root.xpath(query["value"])
