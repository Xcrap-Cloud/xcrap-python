import asyncio
from xcrap.clients import HttpxClient
from xcrap.extractor import HtmlParser


async def main():
    client = HttpxClient()

    print("Testing single fetch...")

    response = await client.fetch(
        url="https://httpbin.org/get",
        method="GET",
        retries=0,
        max_retries=0,
        retry_delay=0,
    )

    response.as_parser(HtmlParser)

    print(f"Status: {response.status}")
    print(f"Body snippet: {response.body[:100]}")

    print("\nTesting fetch_many...")
    # fetch_many now takes individual arguments
    responses = await client.fetch_many(
        requests=[
            {
                "url": "https://httpbin.org/get",
                "method": "GET",
                "retries": 0,
                "max_retries": 0,
                "retry_delay": 0,
            },
            {
                "url": "https://httpbin.org/ip",
                "method": "GET",
                "retries": 0,
                "max_retries": 0,
                "retry_delay": 0,
            },
        ],
        concurrency=2,
        request_delay=0,
    )

    for i, res in enumerate(responses):
        print(f"Response {i} status: {res.status}")


if __name__ == "__main__":
    asyncio.run(main())
