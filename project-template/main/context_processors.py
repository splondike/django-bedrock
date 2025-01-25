"""
Inject template variables
"""

from django.conf import settings
from django.urls import reverse

from main.logging import get_request_id


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
        "js_performance_log_path": reverse("js_performance"),
        "js_request_id": get_request_id(request),
        "js_request_log_probability": settings.JS_REQUEST_LOG_PROB
    }
