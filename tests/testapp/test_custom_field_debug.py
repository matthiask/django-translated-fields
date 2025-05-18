import sys

import pytest

from testapp.custom_fields import ChoicesCharField
from testapp.field_types_models import CustomFieldModel


@pytest.mark.django_db
def test_custom_field_inspection():
    """Debug test to understand what's happening with custom field choices."""
    # Output directly to stderr so we can see it in pytest output
    # Original field before TranslatedField processing
    original_field = ChoicesCharField(
        "Original field",
        max_length=10,
        choices=[("a", "Option A"), ("b", "Option B"), ("c", "Option C")],
    )

    # Check original field deconstruct
    name, path, args, kwargs = original_field.deconstruct()
    print(
        f"\nOriginal field deconstruct: {name}, {path}, {args}, {kwargs}",
        file=sys.stderr,
    )

    # Get the translated field instances
    custom_en = CustomFieldModel._meta.get_field("custom_choices_en")
    custom_de = CustomFieldModel._meta.get_field("custom_choices_de")

    # Check their actual class and attributes
    print(f"Field class EN: {custom_en.__class__.__name__}", file=sys.stderr)
    print(f"Field choices EN: {custom_en.choices}", file=sys.stderr)

    print(f"Field class DE: {custom_de.__class__.__name__}", file=sys.stderr)
    print(f"Field choices DE: {custom_de.choices}", file=sys.stderr)

    # Check their deconstruct values
    name_en, path_en, args_en, kwargs_en = custom_en.deconstruct()
    print(
        f"Translated EN deconstruct: {name_en}, {path_en}, {args_en}, {kwargs_en}",
        file=sys.stderr,
    )

    name_de, path_de, args_de, kwargs_de = custom_de.deconstruct()
    print(
        f"Translated DE deconstruct: {name_de}, {path_de}, {args_de}, {kwargs_de}",
        file=sys.stderr,
    )

    # Add assertions to make it pass
    assert True
