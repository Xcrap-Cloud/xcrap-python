import json

from xcrap.extractor import JsonBaseField, JsonExtractionModel, JsonNestedField, JsonParser, jmes_path

json_data = {
    "title": "Main Project",
    "description": "A demo JSON",
    "tags": ["python", "scraping", "json"],
    "owner": {"name": "Marcuth", "username": "marcuth"},
    "contributors": [{"name": "Alice", "role": "developer"}, {"name": "Bob", "role": "tester"}],
}

content = json.dumps(json_data)


def test_json_parser_extract_value() -> None:
    parser = JsonParser(content)
    assert parser.extract_value(jmes_path("title")) == "Main Project"
    assert parser.extract_value(jmes_path("owner.name")) == "Marcuth"
    assert parser.extract_value(jmes_path("missing"), default="Default") == "Default"


def test_json_parser_extract_values() -> None:
    parser = JsonParser(content)
    assert parser.extract_values(jmes_path("tags")) == ["python", "scraping", "json"]
    assert parser.extract_values(jmes_path("tags"), limit=2) == ["python", "scraping"]


def test_json_extraction_model_basic() -> None:
    class MyModel(JsonExtractionModel):
        title = JsonBaseField(query=jmes_path("title"))
        tags_count = JsonBaseField(query=jmes_path("length(tags)"))

    parser = JsonParser(content)
    data = parser.extract_model(MyModel)

    assert data == {"title": "Main Project", "tags_count": 3}


def test_json_extraction_model_multiple() -> None:
    class MyModel(JsonExtractionModel):
        tags = JsonBaseField(query=jmes_path("tags"), multiple=True)
        first_two_tags = JsonBaseField(query=jmes_path("tags"), multiple=True, limit=2)

    parser = JsonParser(content)
    data = parser.extract_model(MyModel)

    assert data == {"tags": ["python", "scraping", "json"], "first_two_tags": ["python", "scraping"]}


def test_json_extraction_model_nested() -> None:
    class OwnerModel(JsonExtractionModel):
        name = JsonBaseField(query=jmes_path("name"))

    class MyModel(JsonExtractionModel):
        title = JsonBaseField(query=jmes_path("title"))
        owner = JsonNestedField(query=jmes_path("owner"), model=OwnerModel)

    parser = JsonParser(content)
    data = parser.extract_model(MyModel)

    assert data == {"title": "Main Project", "owner": {"name": "Marcuth"}}


def test_json_extraction_model_nested_multiple() -> None:
    class ContributorModel(JsonExtractionModel):
        name = JsonBaseField(query=jmes_path("name"))

    class MyModel(JsonExtractionModel):
        contributors = JsonNestedField(query=jmes_path("contributors"), model=ContributorModel, multiple=True)

    parser = JsonParser(content)
    data = parser.extract_model(MyModel)

    assert data == {"contributors": [{"name": "Alice"}, {"name": "Bob"}]}


def test_json_parser_extract_models() -> None:
    class ContributorModel(JsonExtractionModel):
        name = JsonBaseField(query=jmes_path("name"))

    parser = JsonParser(content)
    data = parser.extract_models(ContributorModel, query=jmes_path("contributors"), limit=1)

    assert data == [{"name": "Alice"}]


def test_json_extraction_model_inheritance() -> None:
    class Base(JsonExtractionModel):
        title = JsonBaseField(query=jmes_path("title"))

    class Child(Base):
        desc = JsonBaseField(query=jmes_path("description"))

    parser = JsonParser(content)
    data = parser.extract_model(Child)

    assert data == {"title": "Main Project", "desc": "A demo JSON"}


def test_json_extraction_model_edge_cases() -> None:
    class MyModel(JsonExtractionModel):
        # Result not a list but multiple=True
        tags = JsonBaseField(query=jmes_path("title"), multiple=True)
        # Nested result not a list but multiple=True
        contributors = JsonNestedField(query=jmes_path("owner"), model=JsonExtractionModel, multiple=True)
        # Non-existent with default
        missing = JsonBaseField(query=jmes_path("missing"), default="Fallback")
        # Non-existent nested with default
        missing_nested = JsonNestedField(query=jmes_path("missing"), model=JsonExtractionModel, default="FallbackNested")

    parser = JsonParser(content)
    data = parser.extract_model(MyModel)

    assert data["tags"] == ["Main Project"]
    assert isinstance(data["contributors"], list)
    assert data["missing"] == "Fallback"
    assert data["missing_nested"] == "FallbackNested"


def test_json_parser_extract_values_non_list() -> None:
    parser = JsonParser(content)
    assert parser.extract_values(jmes_path("title")) == ["Main Project"]
    assert parser.extract_values(jmes_path("missing")) == []


def test_json_parser_extract_models_non_list() -> None:
    class ItemModel(JsonExtractionModel):
        name = JsonBaseField(query=jmes_path("name"))

    parser = JsonParser(content)
    # query returns a dict, not a list
    data = parser.extract_models(ItemModel, query=jmes_path("owner"))
    assert len(data) == 1
    assert data[0] == {"name": "Marcuth"}

    # query returns None
    assert parser.extract_models(ItemModel, query=jmes_path("missing")) == []


def test_json_extraction_model_nested_multiple_with_limit() -> None:
    class ContributorModel(JsonExtractionModel):
        name = JsonBaseField(query=jmes_path("name"))

    class MyModel(JsonExtractionModel):
        # 2 contributors in data, limit to 1
        contributors = JsonNestedField(query=jmes_path("contributors"), model=ContributorModel, multiple=True, limit=1)

    parser = JsonParser(content)
    data = parser.extract_model(MyModel)

    assert len(data["contributors"]) == 1
    assert data["contributors"][0]["name"] == "Alice"
