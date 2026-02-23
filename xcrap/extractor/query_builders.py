from typing import TypedDict


class QueryConfig(TypedDict):
    value: str
    type: str


def css(query: str) -> QueryConfig:
    return {"value": query, "type": "css"}


def xpath(query: str) -> QueryConfig:
    return {"value": query, "type": "xpath"}


__all__ = [
    "css",
    "xpath",
]
