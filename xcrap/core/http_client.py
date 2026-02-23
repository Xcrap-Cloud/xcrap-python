from typing import TypedDict, Optional, Callable
from abc import ABC, abstractmethod
import asyncio

from ..utils.constants import DEFAULT_USER_AGENT
from .http_response import HttpResponse
from ..utils.resolve import resolve

class HttpClientFetchOptions(TypedDict):
    url: str
    method: str
    retries: Optional[int]
    max_retries: Optional[int]
    retry_delay: Optional[int]

class ExecuteRequestOptions(TypedDict):
    index: int
    request: HttpClientFetchOptions
    results: list[HttpResponse | None]
    request_delay: Optional[int]

class HttpClient(ABC):
    def __init__(
        self,
        proxy_url: Optional[str | Callable[[], str]] = None,
        proxy: Optional[str | Callable[[], str]] = None,
        user_agent: Optional[str | Callable[[], str]] = None,
    ) -> None:
        self.proxy_url = proxy_url
        self.proxy = proxy
        self.user_agent = user_agent or DEFAULT_USER_AGENT

    @abstractmethod
    async def fetch(self, url: str, method: str, retries: Optional[int], max_retries: Optional[int], retry_delay: Optional[int]) -> HttpResponse:
        pass

    @abstractmethod
    async def fetch_many(self, requests: list[HttpClientFetchOptions], request_delay: Optional[int], concurrency: Optional[int]) -> list[HttpResponse]:
        pass

    @property
    def _current_proxy_url(self) -> str | None:
        return resolve(self.proxy_url)

    @property
    def _current_proxy(self) -> str | None:
        return resolve(self.proxy)

    @property
    def _current_user_agent(self) -> str:
        return resolve(self.user_agent)

    def _should_throttle(self, executing: list[asyncio.Task], concurrency: Optional[int]) -> bool:
        return concurrency is not None and len(executing) >= concurrency

    def _clean_completed_tasks(self, executing: list[asyncio.Task]) -> None:
        executing[:] = [task for task in executing if not task.done()]

    async def _handle_concurrency(self, executing: list[asyncio.Task]) -> None:
        if not executing:
            return

        await asyncio.wait(executing, return_when=asyncio.FIRST_COMPLETED)

        self._clean_completed_tasks(executing)

    async def _execute_request(self, options: ExecuteRequestOptions) -> None:
        index = options["index"]
        request = options["request"]
        results = options["results"]
        request_delay = options.get("request_delay")

        if request_delay and request_delay > 0 and index > 0:
            await asyncio.sleep(request_delay / 1000)

        results[index] = await self.fetch(**request)

    def _is_success(self, status_code: int) -> bool:
        return status_code >= 200 and status_code < 300