from typing import Any, Dict, Type

from ..extractor.extraction_model import ExtractionModel
from ..extractor.html_extraction_model import HtmlBaseField, HtmlExtractionModel, HtmlNestedField
from ..extractor.json_extraction_model import JsonBaseField, JsonExtractionModel, JsonNestedField
from .extractor_factory import create_extractor


def create_extraction_model(
    model_config: Dict[str, Any],
    allowed_models: Dict[str, Type[ExtractionModel]],
    allowed_extractors: Dict[str, Any],
    extractor_argument_separator: str = ":",
) -> ExtractionModel:
    """
    Creates a parsing model instance from a configuration dictionary.

    Args:
        model_config: A dictionary containing the model 'type' and 'model' schema.
        allowed_models: A dictionary mapping model types to ExtractionModel classes.
        allowed_extractors: A dictionary mapping extractor names to their generators.
        extractor_argument_separator: The character used to split extractor keys from arguments.

    Returns:
        An instantiated ExtractionModel (HtmlExtractionModel or JsonExtractionModel).
    """
    model_type = model_config.get("type")
    if not model_type or model_type not in allowed_models:
        raise ValueError(f"Unsupported model type: '{model_type}'")

    model_class = allowed_models[model_type]
    fields_config = model_config.get("model", {})
    shape = {}

    for field_name, field_data in fields_config.items():
        is_html = issubclass(model_class, HtmlExtractionModel)
        is_json = issubclass(model_class, JsonExtractionModel)

        # Handle extractor
        extractor = None
        if "extractor" in field_data:
            extractor = create_extractor(field_data["extractor"], allowed_extractors, extractor_argument_separator)

        # Handle nested
        if "nested" in field_data:
            nested_model = create_extraction_model(
                field_data["nested"], allowed_models, allowed_extractors, extractor_argument_separator
            )

            if is_html:
                shape[field_name] = HtmlNestedField(
                    query=field_data.get("query"),
                    model=nested_model,
                    limit=field_data.get("limit"),
                    default=field_data.get("default"),
                    multiple=field_data.get("multiple", False),
                    extractor=extractor,
                )
            elif is_json:
                shape[field_name] = JsonNestedField(
                    query=field_data.get("query"),
                    model=nested_model,
                    limit=field_data.get("limit"),
                    default=field_data.get("default"),
                    multiple=field_data.get("multiple", False),
                )
        else:
            # Base field
            if is_html:
                shape[field_name] = HtmlBaseField(
                    query=field_data.get("query"),
                    default=field_data.get("default"),
                    multiple=field_data.get("multiple", False),
                    limit=field_data.get("limit"),
                    extractor=extractor,
                )
            elif is_json:
                shape[field_name] = JsonBaseField(
                    query=field_data.get("query"),
                    default=field_data.get("default"),
                    multiple=field_data.get("multiple", False),
                    limit=field_data.get("limit"),
                )

    return model_class(shape=shape)
