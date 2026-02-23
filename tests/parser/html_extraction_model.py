from xcrap.extractor import HtmlParser, HtmlExtractionModel, HtmlBaseField, HtmlNestedField
from xcrap.extractor.query_builders import css

parser = HtmlParser("""
<html>
<head>
    <title>Document</title>
</head>
<body>
    <h1 class="title">This is a heading</h1>
    <p id="description">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras egestas justo nunc, vitae aliquam augue rhoncus congue. Nulla vel urna turpis. Mauris sagittis ullamcorper lacinia. Ut ut elit at mauris auctor vulputate sit amet nec tortor. Aliquam rutrum sollicitudin massa, id semper velit vulputate sed. Maecenas in porttitor justo, non laoreet libero. In non lacus et velit pulvinar pretium eget id metus. Donec eget vehicula massa, et mattis sem. Sed magna eros, dapibus eget scelerisque vel, tincidunt at ante. Nunc tempus risus felis, non porttitor nibh laoreet et. Aliquam vitae lorem quis orci tincidunt ultricies. Fusce euismod tristique augue, eget malesuada justo mollis eget. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.</p>
    <ul class="list">
        <li class="item">Item 1</li>
        <li class="item">Item 2</li>
        <li class="item">Item 3</li>
        <li class="item">Item 4</li>
    </ul>
</body>
</html>
""")

def test_html_extraction_model_should_exists() -> None:
    assert HtmlExtractionModel
    
def test_html_base_field_should_exists() -> None:
    assert HtmlBaseField
    
def test_html_nested_field_should_exists() -> None:
    assert HtmlNestedField

def test_html_extraction_model_should_extract_single_base_fields() -> None:
    expected = {
        "title": "This is a heading",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras egestas justo nunc, vitae aliquam augue rhoncus congue. Nulla vel urna turpis. Mauris sagittis ullamcorper lacinia. Ut ut elit at mauris auctor vulputate sit amet nec tortor. Aliquam rutrum sollicitudin massa, id semper velit vulputate sed. Maecenas in porttitor justo, non laoreet libero. In non lacus et velit pulvinar pretium eget id metus. Donec eget vehicula massa, et mattis sem. Sed magna eros, dapibus eget scelerisque vel, tincidunt at ante. Nunc tempus risus felis, non porttitor nibh laoreet et. Aliquam vitae lorem quis orci tincidunt ultricies. Fusce euismod tristique augue, eget malesuada justo mollis eget. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas."
    }
    
    class MyExtractionModel(HtmlExtractionModel):
        title = HtmlBaseField(
            query = css("h1.title::text")
        )
        description = HtmlBaseField(
            query = css("p#description::text")
        )
        
    data = parser.extract_model(MyExtractionModel)
    
    assert expected["title"] == data["title"]
    assert expected["description"] == data["description"]
    
def test_html_extraction_model_should_return_default_value_when_element_dont_exists() -> None:
    expected = {
        "xpto": "DEFAULT_VALUE"
    }
    
    class MyExtractionModel(HtmlExtractionModel):
        xpto = HtmlBaseField(
            query = css(".xpto"),
            default = "DEFAULT_VALUE"
        )
        
    data = parser.extract_model(MyExtractionModel)
    
    assert expected["xpto"] == data["xpto"]
    
def test_html_extraction_model_should_extract_multiple_base_fields() -> None:
    expected = {
        "items": ["Item 1", "Item 2", "Item 3", "Item 4"]
    }
    
    class MyExtractionModel(HtmlExtractionModel):
        items = HtmlBaseField(
            query = css("ul.list li.item::text"),
            multiple = True
        )
        
    data = parser.extract_model(MyExtractionModel)
    
    assert expected["items"] == data["items"]
    
def test_html_extraction_model_should_extract_multiple_base_fields_with_limit() -> None:
    expected = {
        "items": ["Item 1", "Item 2"]
    }
    
    class MyExtractionModel(HtmlExtractionModel):
        items = HtmlBaseField(
            query = css("ul.list li.item::text"),
            multiple = True,
            limit = 2
        )
        
    data = parser.extract_model(MyExtractionModel)
    
    assert expected["items"] == data["items"]