"""
Error views
"""

from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseNotFound,
    HttpResponseForbidden
)
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.template import TemplateDoesNotExist, loader
from django.views.defaults import (
    ERROR_400_TEMPLATE_NAME,
    ERROR_403_TEMPLATE_NAME,
    ERROR_404_TEMPLATE_NAME,
    ERROR_500_TEMPLATE_NAME
)

from main.logging import get_request_id


def render_error_page(request: HttpRequest, template_name: str, request_class):
    """
    Something like the built in error handlers, but with more context for the
    template.

    See django.views.defaults.bad_request
    """
    accepts_html = request.accepts("text/html")
    accepts_json = request.accepts("application/json")

    message = "Unhandled server error"
    code = 500
    if request_class == HttpResponseServerError:
        message = "General server error"
        code = 500
    elif request_class == HttpResponseBadRequest:
        message = "General error with request"
        code = 400
    elif request_class == HttpResponseForbidden:
        message = "Forbidden"
        code = 403
    elif request_class == HttpResponseNotFound:
        message = "Resource not found"
        code = 404
    else:
        message = "Unhandled server error"
        code = 500

    if accepts_html or not accepts_json:
        try:
            template = loader.get_template(template_name)
        except TemplateDoesNotExist:
            return request_class(
                f"<h1>{message} ({code})</h1>",
                content_type="text/html"
            )
        return request_class(
            template.render({
                "request": request,
                "url": request.build_absolute_uri(),
                "js_request_id": get_request_id(request),
                # Turn these off for now
                "js_error_log_path": "",
                "js_error_log_probability": "0.0",
                "js_request_log_probability": "0.0",
                "js_performance_log_path": "",
            }),
            content_type="text/html"
        )
    else:
        return JsonResponse({
            "errors": [
                {
                    "status": code,
                    "title": message,
                }
            ]
        }, code=code)


def server_error(request, template_name=ERROR_500_TEMPLATE_NAME):
    return render_error_page(request, template_name, HttpResponseServerError)


def bad_request(request, exception, template_name=ERROR_400_TEMPLATE_NAME):
    return render_error_page(request, template_name, HttpResponseBadRequest)


def not_found(request, exception, template_name=ERROR_404_TEMPLATE_NAME):
    return render_error_page(request, template_name, HttpResponseNotFound)


def forbidden(request, exception, template_name=ERROR_403_TEMPLATE_NAME):
    return render_error_page(request, template_name, HttpResponseForbidden)
