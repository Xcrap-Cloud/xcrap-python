from xcrap.extractor import QueryConfig, css, xpath

def test_query_config_should_exists() -> None:
    assert QueryConfig

def test_css_query_builder_should_exists() -> None:
    assert css
    
def test_xpath_query_builder_should_exists() -> None:
    assert xpath

def test_css_query_builder() -> None:
    input = "span"
    expected = { "type": "css", "value": input }
    
    data = css(input)
    
    assert expected == data
    
def test_xpath_query_builder() -> None:
    input = "//span"
    expected = { "type": "xpath", "value": input }
    
    data = xpath(input)
    
    assert expected == data
    