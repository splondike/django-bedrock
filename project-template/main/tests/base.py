"""
Miscellaneous helpers pertaining to automated tests
"""
import pytest
from django.test import Client


@pytest.mark.django_db
class StandardClientTestCase:
    """
    Base class for most tests that use the Django Client
    """

    @pytest.fixture(autouse=True)
    def template_settings(self, settings):
        opts = settings.TEMPLATES[0]["OPTIONS"]
        opts["string_if_invalid"] = InvalidVarException()
        opts["debug"] = True

    def setup_method(self, method):
        self.client = Client()


class InvalidVarException(str):
    """
    Raise an exception when a context variable isn't found while rendering
    a template.

    From
    https://www.vinta.com.br/blog/2017/dont-forget-stamps-testing-email-content-django/
    """
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, "%s")

    def __mod__(self, missing):
        try:
            missing_str = str(missing)
        except Exception:
            missing_str = "Failed to create string representation"
        raise Exception("Unknown template variable %r %s" %
                        (missing, missing_str))

    def __contains__(self, search):
        return True
