from typing import Any, Callable, Dict

from parsel import Selector

ExtractorFunction = Callable[[Selector], Any]


def create_extractor(
    extractor_text: str, allowed_extractors: Dict[str, Callable], argument_separator: str = ":"
) -> ExtractorFunction:
    """
    Creates an extractor function from the specified text mapping or generator.

    Args:
        extractor_text: The string identifier for the extractor (optionally with arguments).
        allowed_extractors: A dictionary mapping identifiers to extractor generators.
        argument_separator: The character used to separate the identifier from arguments.

    Returns:
        A callable function that takes a Selector and returns the extracted data.
    """
    if argument_separator in extractor_text:
        key, *args = extractor_text.split(argument_separator)
        if key not in allowed_extractors:
            raise ValueError(f"'{key}' is not an allowed extractor!")

        generator = allowed_extractors[key]
        return generator(*args)

    if extractor_text not in allowed_extractors:
        raise ValueError(f"'{extractor_text}' is not an allowed extractor!")

    generator = allowed_extractors[extractor_text]
    # In some cases the extractor might be the function itself if it takes no args,
    # or it might be a generator that needs to be called.
    # To match TS, we assume it's a generator that returns the extractor function.
    return generator()
