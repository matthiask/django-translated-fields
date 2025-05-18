from django.db import models


class ChoicesCharField(models.CharField):
    """
    CharField with hardcoded default choices in deconstruct() method.

    Similar to feincms3.utils.ChoicesCharField, this field sets a default set of
    choices in the deconstruct method to avoid migrations when choices change.
    """

    def __init__(self, *args, **kwargs):
        # Non-empty choices for get_*_display
        kwargs.setdefault("choices", [("", "")])
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Always return hardcoded choices in deconstruct - this is what we want to test
        # TranslatedField should preserve the runtime choices, not the ones from deconstruct
        kwargs["choices"] = [("", "")]
        return name, path, args, kwargs
