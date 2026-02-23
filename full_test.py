from xcrap.extractor import HtmlExtractionModel, HtmlBaseField, HtmlNestedField, css
from xcrap.clients import HttpxClient
import asyncio


class AuthorModel(HtmlExtractionModel):
    name = HtmlBaseField(query=css("small.author::text"))
    link = HtmlBaseField(query=css("a::attr(href)"))


class QuoteModel(HtmlExtractionModel):
    text = HtmlBaseField(query=css("span.text::text"))
    author = HtmlNestedField(model=AuthorModel)
    tags = HtmlBaseField(query=css("div.tags a.tag::text"), multiple=True)


class QuotesPageModel(HtmlExtractionModel):
    quotes = HtmlNestedField(query=css("div.quote"), model=QuoteModel, multiple=True)


async def main():
    client = HttpxClient()

    print("Fetching http://quotes.toscrape.com ...")

    # 2. Fetch the page
    response = await client.fetch(url="http://quotes.toscrape.com", method="GET")

    if not response.is_success():
        print(f"Failed to fetch page: {response.status}")
        return

    # 3. Use the parser to extract data using the model
    # We can use the as_parser method from the response
    parser = response.as_html_parser()

    # Extract the data
    data = parser.extract_model(QuotesPageModel)

    print("\nExtracted Data:")
    for i, quote in enumerate(data["quotes"][:3]):  # Show first 3
        print(f"\nQuote {i + 1}:")
        print(f"  Text: {quote['text']}")
        print(f"  Author: {quote['author']}")
        print(f"  Tags: {', '.join(quote['tags'])}")

    # Basic Verifications
    assert len(data["quotes"]) > 0
    assert "text" in data["quotes"][0]
    assert "author" in data["quotes"][0]
    print("\nFull test passed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
