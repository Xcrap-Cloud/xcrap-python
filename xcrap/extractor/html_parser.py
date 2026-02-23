"""
import htmlParser, { HTMLElement, Options as NodeHtmlOptions } from "node-html-parser"

import { selectFirstElement, selectManyElements } from "../utils"
import { ExtractionModel } from "../interfaces/extraction-model"
import { HTMLElementNotFoundError } from "../errors"
import { BuildedQuery } from "../query-builders"
import { ExtractorFunction } from "./extractors"
import { SourceParser } from "../source-parser"

export type ExtractValuesOptions = {
    query: BuildedQuery
    extractor: ExtractorFunction
    limit?: number
}

export type ExtractValueOptions = {
    query?: BuildedQuery
    extractor: ExtractorFunction
    default?: string | null
}

export type ExtractModelOptions<T = any> = {
    query?: BuildedQuery
    model: ExtractionModel<T>
}

export type ExtractModelsOptions<T = any> = {
    query: BuildedQuery
    model: ExtractionModel<T>
    limit?: number
}

export const nodeHtmlParserOptions = {
    blockTextElements: {
        script: true,
        noscript: true,
        style: true,
        code: true,
    },
} satisfies NodeHtmlOptions

export class HtmlParser extends SourceParser {
    readonly root: HTMLElement

    constructor(
        readonly source: string,
        options: NodeHtmlOptions = nodeHtmlParserOptions,
    ) {
        super(source)

        this.root = htmlParser.parse(source, options)
    }

    async extractValues({ query, extractor, limit }: ExtractValuesOptions): Promise<(string | undefined)[]> {
        const elements = selectManyElements(query, this.root)

        let items: (string | undefined)[] = []

        for (const element of elements) {
            if (limit != undefined && items.length >= limit) break
            const data = await extractor(element)
            items.push(data)
        }

        return items
    }

    async extractValue({ query, extractor, default: default_ }: ExtractValueOptions): Promise<any | undefined | null> {
        let data: any | undefined | null

        if (query) {
            const element = selectFirstElement(query, this.root)

            if (!element) {
                if (default_ !== undefined) {
                    return default_
                }

                throw new HTMLElementNotFoundError(query)
            }

            data = await extractor(element)
        } else {
            data = await extractor(this.root)
        }

        return data ?? default_
    }

    async extractModel<T>({ model, query }: ExtractModelOptions<T>): Promise<T> {
        const element = query ? selectFirstElement(query, this.root) : this.root

        if (!element) {
            throw new HTMLElementNotFoundError(query)
        }

        return await model.extract(element.outerHTML)
    }

    async extractModels<T>({ model, query, limit }: ExtractModelsOptions<T>): Promise<T[]> {
        const elements = selectManyElements(query, this.root)

        let dataList: any[] = []

        for (const element of elements) {
            if (limit != undefined && dataList.length >= limit) break
            const data = await model.extract(element.outerHTML)
            dataList.push(data)
        }

        return dataList
    }
}
"""

from parsel import Selector
from typing import Optional, Any

from .query_builders import QueryConfig
from .source_parser import SourceParser

class HtmlParser(SourceParser):
    def __init__(self, content: str) -> None:
        self.selector = Selector(text=content)

    def extract_value(self, query: QueryConfig, default: Optional[str] = None) -> Optional[str]:
        elements = self._select_elements(query)
        result = elements.get()
        return result if result is not None else default

    def extract_values(self, query: QueryConfig, limit: Optional[int] = None) -> list[str]:
        elements = self._select_elements(query)
        if limit is not None:
            elements = elements[:limit]
        return elements.getall()

    def extract_model(self, model: any, query: Optional[QueryConfig] = None) -> Any:
        element = self._select_elements(query)[0] if query else self.selector
        return model.extract(element)

    def extract_models(self, model: any, query: QueryConfig, limit: Optional[int] = None) -> list[Any]:
        elements = self._select_elements(query)
        if limit is not None:
            elements = elements[:limit]
        
        return [model.extract(el) for el in elements]

    def _select_elements(self, query: QueryConfig):
        if query["type"] == "css":
            return self.selector.css(query["value"])
            
        return self.selector.xpath(query["value"])
