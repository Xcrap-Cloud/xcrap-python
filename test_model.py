from xcrap.extractor import HtmlBaseField, HtmlExtractionModel, HtmlNestedField, css


class AuthorModel(HtmlExtractionModel):
    name = HtmlBaseField(query=css("span.author-name::text"))


class PostModel(HtmlExtractionModel):
    title = HtmlBaseField(
        query=css("h1::text"),
    )
    tags = HtmlBaseField(query=css("ul.tags li::text"), multiple=True)
    author = HtmlNestedField(query=css("div.author-info"), model=AuthorModel)
    link = HtmlBaseField(query=css("a.source::attr(href)"))


def test_extraction():
    html = """
    <html>
        <body>
            <h1>Hello World</h1>
            <ul class="tags">
                <li>Python</li>
                <li>Scraping</li>
            </ul>
            <div class="author-info">
                <span class="author-name">John Doe</span>
            </div>
            <a class="source" href="https://example.com">Source</a>
        </body>
    </html>
    """

    # 2. Just instantiate and extract!
    model = PostModel()
    result = model.extract(html)

    print(f"Extraction result: {result}")

    # Verification
    assert result["title"] == "Hello World"
    assert result["tags"] == ["Python", "Scraping"]
    assert result["author"]["name"] == "John Doe"
    assert result["link"] == "https://example.com"
    print("Test passed!")


if __name__ == "__main__":
    test_extraction()
