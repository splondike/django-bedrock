"""
Classes to help you make a JSON:API based API.

See https://jsonapi.org/format/
"""
import json
from typing import Any, Dict, List, Optional

from django import forms
from django.http import HttpRequest, JsonResponse


class ApiResponse(JsonResponse):
    """
    Base API response class. See 
    - data - https://jsonapi.org/format/#document-resource-objects
    - Errors - https://jsonapi.org/format/#error-objects
    - Links - https://jsonapi.org/format/#document-links
    """
    def __init__(self, data: Optional[Any]=None, errors: Optional[List]=None, links: Optional[Any]=None, **kwargs):
        kwargs.setdefault("content_type", "application/vnd.api+json")

        if data:
            assert errors is None
            content = {
                "data": data
            }
        elif errors:
            assert data is None
            content = {
                "errors": errors
            }
        else:
            raise AssertionError(
                "Must specify either data or errors keys."
            )

        if links:
            content["links"] = links

        super().__init__(
            data=content,
            **kwargs,
        )


class SimpleErrorResponse(ApiResponse):
    """
    A basic message and error code (same as HTTP status) response
    """

    def __init__(self, message: str, status: int=500, **kwargs):
        super().__init__(
            errors=[
                {
                    "status": str(status),
                    "title": self._calculate_title(status),
                    "detail": message,
                }
            ],
            status=status
        )

    def _calculate_status(self, status: int):
        if status == 500:
            return "internal_server_error"
        elif status == 405:
            return "method_not_allowed"
        elif status == 404:
            return "not_found"
        elif status == 403:
            return "forbidden"
        elif status == 400:
            return "bad_request"
        else:
            raise ValueError(f"Unknown status code {status}")


class FormApiMixin:
    """
    Validate the request and return a nicely formatted JSON:API error response if it doesn't pass the validation in a form.

    Uses similar naming to django.views.generic.edit.{FormMixin, ProcessFormView} to make navigating the code more familiar.

    Can source form data from the URL path, headers, query parameters, or a decoded JSON post.

    Form data defaults to coming from data.attributes keys as per JSON:API https://jsonapi.org/format/#crud-creating
    but that can be overridden by setting:

        field_data_sources = {
            # The field called object_id will be populated from the path capture called 'object_id'
            "object_id": ("path", "object_id"),
            # The field called my_header will be populated from the HTTP header 'My-Header'
            "my_header": ("header", "My-Header"),
            # The field called query_field will be populated from the query parameters 'query_field'
            "query_field": ("query", "query_field"),
            # The field called body_field will be populated from the decoded JSON body at the given JSON pointer path
            # see https://datatracker.ietf.org/doc/html/rfc6901#section-5
            "body_field": ("body", "/data/attributes/foo"),
        }

    """

    form_class = None
    # Only accept POST requests by default, override this to "put", or "delete" as needed in subclasses
    http_method_names = [
        "post"
    ]
    # Set this to override where form data gets populated from
    field_data_sources = None

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs(form_fields=form_class.base_fields))

    def get_field_data_sources(self, form_fields=None):
        default_sources = {
            key: ("body", f"/data/attributes/{key}")
            for key in (form_fields.keys() if form_fields else [])
        }
        default_sources.update(self.field_data_sources)
        return default_sources

    def get_form_kwargs(self, form_fields=None):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {}

        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.get_form_data(form_fields=form_fields),
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def get_form_data(self, form_fields):
        """
        Get data for the form from the request
        """

        request = self.request
        body_cache = None
        def _body():
            nonlocal body_cache
            if body_cache is None:
                body_cache = json.loads(request.body)
            return body_cache

        def _get(source, source_qualifier):
            if source == "path":
                # I'm making it an error if this one is missing since that's a programmer error
                return request.request_path_args[source_qualifier]
            elif source == "header":
                return request.headers.get(source_qualifier)
            elif source == "query":
                return request.GET.get(source_qualifier)
            elif source == "body":
                try:
                    return extract_json_path(source_qualifier, _body())
                except KeyError:
                    return None
            else:
                raise RuntimeError("Invalid _data_sources source: " + source)

        return {
            field_name: _get(source, source_qualifier)

            for field_name, (source, source_qualifier) in self.get_field_data_sources(form_fields).items()
        }

    def form_valid(self, form):
        """If the form is valid return success."""

        raise NotImplementedError

    def form_invalid(self, form):
        """If the form is invalid let the caller know the errors."""

        field_data_sources = self.get_field_data_sources(form_fields=form.fields)

        return ApiResponse(
            errors=[
                self.build_api_validation_error(field_data_sources, field_name, error)

                for field_name, errors in form.errors.items()
                for error in errors
            ],
            status=400
        )

    @classmethod
    def build_api_validation_error(cls, field_data_sources: list, field_name: str, error: str) -> Dict[str, Any]:
        return {
            "status": 400,
            "title": "Invalid request parameter",
            "detail": error,
            "source": cls.get_field_source(field_data_sources, field_name)
        }

    @classmethod
    def get_field_source(cls, field_data_sources: list, field_name: str) -> Dict[str, str]:
        """
        Turns a form field into a JSON:API 'source' as described here: https://jsonapi.org/format/#error-objects
        """
        source, source_qualifier = field_data_sources[field_name]
        if source == "path":
            return {
                "path": source_qualifier
            }
        elif source == "header":
            return {
                "header": source_qualifier
            }
        elif source == "query":
            return {
                "parameter": source_qualifier
            }
        elif source == "body":
            return {
                "pointer": f"{source_qualifier}"
            }

        raise RuntimeError(f"Could not find source data for field_name: {field_name}")

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        request.request_path_args = kwargs
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.post(*args, **kwargs)


def extract_json_path(path: str, obj: Any) -> Any:
    """
    Attempts to extract data from the given object based on the JSONPath
    in path. Throws a KeyError if it can't find it. Throws a ValueError if
    the JSON path is invalid.

    See https://datatracker.ietf.org/doc/html/rfc6901#section-3
    """
    curr_obj = obj
    startpos = 0
    endpos = 0
    while endpos < len(path)-1:
        for endpos in range(startpos+1, len(path)+1):
            if endpos == len(path) or path[endpos] == "/":
                break

        matcher = path[startpos+1:endpos].replace("~1", "/").replace("~0", "~")
        try:
            num_matcher = int(matcher)
        except ValueError:
            num_matcher = None
        if num_matcher is not None:
            if not isinstance(curr_obj, list):
                raise KeyError(f"Item at pos {startpos} in \"{path}\" does not point to a list")
            if (len(curr_obj) - 1) < num_matcher:
                raise KeyError(f"Item at pos {startpos} in \"{path}\" too large for list")

            curr_obj = curr_obj[num_matcher]
            startpos = endpos
        elif matcher in curr_obj:
            curr_obj = curr_obj[matcher]
            startpos = endpos
        else:
            raise KeyError(f"Couldn't find item at pos {startpos} in \"{path}\"")

    return curr_obj
