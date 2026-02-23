from typing import Callable, Optional, TypeVar

T = TypeVar("T")


def resolve(value: Optional[T] | Callable[[], T]) -> T:
    if value is None:
        return None

    if callable(value):
        return value()

    return value
