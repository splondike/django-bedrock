"""
Error views
"""

from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseNotFound
)
from django.template import TemplateDoesNotExist, loader

from django.views.defaults import (
    ERROR_400_TEMPLATE_NAME,
    ERROR_404_TEMPLATE_NAME,
    ERROR_500_TEMPLATE_NAME
)


def render_error_page(request, template_name, request_class):
    """
    Something like the built in error handlers, but with more context for the
    template.

    See django.views.defaults.bad_request
    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return request_class(
            "<h1>Server error</h1>",
            content_type="text/html"
        )
    return request_class(
        template.render({
            "url": request.build_absolute_uri()
        }),
        content_type="text/html"
    )


def server_error(request, template_name=ERROR_500_TEMPLATE_NAME):
    return render_error_page(request, template_name, HttpResponseServerError)


def bad_request(request, exception, template_name=ERROR_400_TEMPLATE_NAME):
    return render_error_page(request, template_name, HttpResponseBadRequest)


def not_found(request, exception, template_name=ERROR_404_TEMPLATE_NAME):
    return render_error_page(request, template_name, HttpResponseNotFound)
