from typing import Any, Dict, Type

from ..core.http_client_base import HttpClientBase


def create_client(
    client_type: str, allowed_clients: Dict[str, Type[HttpClientBase]], options: Dict[str, Any]
) -> HttpClientBase:
    """
    Creates a client instance of the specified type from the allowed clients dictionary.
    """
    if client_type not in allowed_clients:
        raise ValueError(f"'{client_type}' is not a valid type of client!")

    client_class = allowed_clients[client_type]
    return client_class(**options)
