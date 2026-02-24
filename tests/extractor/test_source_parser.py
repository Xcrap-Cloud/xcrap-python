from xcrap.extractor import SourceParser

def test_source_parser_should_defined() -> None:
    assert SourceParser
    
def test_init_source_parser() -> None:
    input = "xpto"
    parser = SourceParser(input)
    
    assert parser.content == input
    
def test_init_with_file_loading(tmp_path: str) -> None:
    file_path = tmp_path / "example.txt"
    file_path.write_text("xpto")

    parser = SourceParser.load_file(str(file_path))

    assert parser.content == "xpto"