"""
Inject template variables
"""

from django.conf import settings
from django.urls import reverse


def debug(request):
    """
    Template variable for if we're in debug mode. There's a built in one based
    on INTERNAL_IPs, but that seems too annoying given we're using nginx.
    """

    rtn = {}
    if settings.DEBUG:
        rtn["debug"] = True

    return rtn


def frontend_logging(request):
    """
    Info for frontend logging scripts
    """

    return {
        "js_error_log_path": reverse("js_error"),
        "js_error_log_probability": settings.JS_ERROR_LOG_PROB
    }
