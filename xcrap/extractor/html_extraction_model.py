"""
import htmlParser, { HTMLElement, Options as NodeHtmlOptions } from "node-html-parser"

import { MultipleQueryError, HTMLElementNotFoundError } from "../errors"
import { selectManyElements, selectFirstElement } from "../utils"
import { ExtractionModel } from "../interfaces/extraction-model"
import { BuildedQuery } from "../query-builders"
import { ExtractorFunction } from "./extractors"
import { nodeHtmlParserOptions } from "./parser"

export type HtmlExtractionModelShapeBaseValue = {
    query?: BuildedQuery
    default?: string | string[] | null
    multiple?: boolean
    limit?: number
    extractor: ExtractorFunction
}

export type HtmlExtractionModelShapeNestedValue = {
    query: BuildedQuery
    limit?: number
    default?: any | any[]
    multiple?: boolean
    model: ExtractionModel
    extractor?: ExtractorFunction
}

export type HtmlExtractionModelValue = HtmlExtractionModelShapeBaseValue | HtmlExtractionModelShapeNestedValue

export type HtmlExtractionModelShape = {
    [key: string]: HtmlExtractionModelValue
}

export type InferHtmlValue<V extends HtmlExtractionModelValue> = V extends HtmlExtractionModelShapeNestedValue
    ? V["multiple"] extends true
        ? V["model"] extends ExtractionModel<infer M>
            ? M[]
            : any
        : V["model"] extends ExtractionModel<infer M>
          ? M
          : any
    : V extends HtmlExtractionModelShapeBaseValue
      ? V["multiple"] extends true
          ? Awaited<ReturnType<V["extractor"]>>[]
          : Awaited<ReturnType<V["extractor"]>>
      : never

export type InferHtmlShape<S extends HtmlExtractionModelShape> = {
    [K in keyof S]: InferHtmlValue<S[K]>
}

export type ParseBaseValueReturnType = (undefined | string)[] | string | null | undefined

export class HtmlExtractionModel<S extends HtmlExtractionModelShape> implements ExtractionModel<InferHtmlShape<S>> {
    constructor(readonly shape: S) {}

    async extract(source: string, options: NodeHtmlOptions = nodeHtmlParserOptions): Promise<InferHtmlShape<S>> {
        const root = htmlParser.parse(source, options)
        const data: any = {}

        for (const key in this.shape) {
            const value = this.shape[key]

            const isNestedValue = "model" in value

            if (isNestedValue) {
                data[key] = await this.extractNestedValue(value, root)
            } else {
                data[key] = await this.extractBaseValue(value, root)
            }
        }

        return data
    }

    protected async extractBaseValue(
        value: HtmlExtractionModelShapeBaseValue,
        root: HTMLElement,
    ): Promise<ParseBaseValueReturnType> {
        if (value.multiple) {
            if (!value.query) {
                throw new MultipleQueryError()
            }

            const elements = selectManyElements(value.query, root)

            if (value.limit !== undefined) {
                elements.splice(value.limit)
            }

            return await Promise.all(elements.map((element) => value.extractor(element)))
        } else {
            const element = value.query ? selectFirstElement(value.query, root) : root

            if (!element) {
                if (value.default === undefined) {
                    throw new HTMLElementNotFoundError(value.query)
                }

                return value.default
            }

            return await value.extractor(element)
        }
    }

    protected async extractNestedValue(value: HtmlExtractionModelShapeNestedValue, root: HTMLElement) {
        if (value.multiple) {
            const elements = selectManyElements(value.query, root)

            if (value.limit !== undefined) {
                elements.splice(value.limit)
            }

            return await Promise.all(elements.map((element) => value.model.extract(element.outerHTML)))
        } else {
            const element = selectFirstElement(value.query, root)

            if (!element) {
                if (value.default === undefined) {
                    throw new HTMLElementNotFoundError(value.query)
                }

                return value.default
            }

            const source = value.extractor ? ((await value.extractor(element)) as string) : element.outerHTML

            const data = await value.model.extract(source)

            return data
        }
    }
}
"""

from typing import Any, Dict, List, Optional, Union, Type
from parsel import Selector
from pydantic import BaseModel

from .extracton_model import ExtractionModel
from .query_builders import QueryConfig

class HtmlBaseField(BaseModel):
    """Configuration for extracting a basic value (string, attribute, etc.)"""
    query: QueryConfig
    default: Optional[Any] = None
    multiple: bool = False
    limit: Optional[int] = None

class HtmlNestedField(BaseModel):
    """Configuration for extracting a nested model structure"""
    query: QueryConfig
    model: Union[ExtractionModel, Type[ExtractionModel]]
    limit: Optional[int] = None
    default: Optional[Any] = None
    multiple: bool = False
    
    # Allow ExtractionModel which is an ABC/Interface
    model_config = {"arbitrary_types_allowed": True}

# The Union of possible shape values
HtmlExtractionField = Union[HtmlBaseField, HtmlNestedField]

class HtmlExtractionModel(ExtractionModel):
    """
    Model for extracting structured data from HTML source using CSS/XPath selectors.
    Supports both declarative (class-based) and dynamic (shape-based) definitions.
    """
    _fields: Dict[str, HtmlExtractionField] = {}

    def __init__(self, shape: Optional[Dict[str, HtmlExtractionField]] = None) -> None:
        # If shape is provided, use it. Otherwise, use fields defined on the class.
        self.shape = shape if shape is not None else self._fields

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Collect all HtmlFields defined as class attributes
        fields = {}
        for name, attr in cls.__dict__.items():
            if isinstance(attr, (HtmlBaseField, HtmlNestedField)):
                fields[name] = attr
        
        # Merge with parent fields if any
        combined_fields = {}
        for base in reversed(cls.__mro__):
            if hasattr(base, "_fields"):
                combined_fields.update(base._fields)
        
        combined_fields.update(fields)
        cls._fields = combined_fields

    def extract(self, content: str | Selector) -> Dict[str, Any]:
        """
        Extract data from the provided HTML content or Selector.
        """
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
                elements = elements[:value.limit]
            
            results = elements.getall()
            return results if results else (value.default if value.default is not None else [])
        else:
            result = elements.get()
            if result is None:
                return value.default
            return result

    def _extract_nested_value(self, value: HtmlNestedField, root: Selector) -> Any:
        elements = self._select_elements(value.query, root)

        # Handle class-based models by instantiating them
        model = value.model
        if isinstance(model, type):
            model = model()

        if value.multiple:
            if value.limit is not None:
                elements = elements[:value.limit]

            results = []
            for el in elements:
                results.append(model.extract(el))
            
            return results if results else (value.default if value.default is not None else [])
        else:
            element = elements[0] if len(elements) > 0 else None

            if element is None:
                return value.default

            return model.extract(element)

    def _select_elements(self, query: QueryConfig, root: Selector):
        if query["type"] == "css":
            return root.css(query["value"])
        return root.xpath(query["value"])

