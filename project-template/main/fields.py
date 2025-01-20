import uuid_extensions
from django.db import models


class UUID7Field(models.UUIDField):
    """
    Specialisation of UUIDField to use UUID7s which work better
    with database indexes.

    In theory in the future we could set DEFAULT_AUTO_FIELD to
    this and have models automatically use it, but there's a
    technical limitation in Django currently preventing that.
    """

    def __init__(self, verbose_name=None, **kwargs):
        kwargs["max_length"] = 32
        kwargs["default"] = kwargs.get("default", self.uuid7)
        super().__init__(verbose_name, **kwargs)

    @staticmethod
    def uuid7(**kwargs):
        """
        Generates a UUID using the UUID7 algorithm.
        """
        # Wrapping the uuid_extensions function because the django makemigrations command doesn't produce
        # code that works with uuid_extensions. It generates uuid_extensions.uuid7.uuid7 which points to
        # a non-existant property of the generator function rather than the function itself. So for
        # ergonomics I do this wrapping.

        return uuid_extensions.uuid7(**kwargs)
