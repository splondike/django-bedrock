"""
Custom Django system checks.

See https://docs.djangoproject.com/en/5.0/topics/checks/
"""

from django.conf import settings
from django.core.checks import Warning, register
from django.urls.resolvers import URLPattern, URLResolver

from main.auth.mixins import PermissionRequiredMixin, LoginNotRequiredMixin


def get_all_view_classes(urlpatterns=None):
    if urlpatterns is None:
        root_urlconf = __import__(settings.ROOT_URLCONF)
        urlpatterns = root_urlconf.urls.urlpatterns

    rtn = []

    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            if hasattr(pattern.callback, "view_class"):
                rtn.append(pattern.callback.view_class)
            else:
                # All the pure function views we use don't need
                # auth, so ignore them
                pass
        elif isinstance(pattern, URLResolver):
            for cls in get_all_view_classes(pattern.url_patterns):
                rtn.append(cls)
        else:
            raise RuntimeError("Couldn't process pattern: " + str(pattern))
    return rtn


@register()
def view_authentication_check(app_configs, **kwargs):
    """
    Checks that all Views are either authenticated or explicitly
    marked as not needing it.
    """

    rtn = []
    for cls in get_all_view_classes():
        superclasses = cls.__mro__
        passes_check = (
            not cls.__module__.startswith("main.") or
            PermissionRequiredMixin in superclasses or
            LoginNotRequiredMixin in superclasses
        )
        if not passes_check:
            rtn.append(
                Warning(
                    "Class based view not explicitly marked as requiring or not requiring authentication",
                    hint="Add PermissionRequiredMixin or LoginNotRequiredMixin to class hierarchy",
                    obj=cls,
                    id="main.authcheck"
                )
            )

    return rtn
