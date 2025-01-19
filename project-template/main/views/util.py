import os
import socket
import logging

from django.conf import settings
from django.db import connection
from django.http import Http404
from django.views import View
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_page

from main.auth.mixins import LoginNotRequiredMixin


LOGGER = logging.getLogger(__name__)


# Cache response in case some of the checks are expensive
@method_decorator(cache_page(30), name="dispatch")
class HealthcheckView(LoginNotRequiredMixin, View):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        if len(request.GET) > 0:
            # Don't allow people to bypass the cache
            raise Http404

        healthchecks = {
            "health_db": self._get_health_db(),
        }
        is_error = any([r == "FAIL" for r in healthchecks.values()])
        return JsonResponse(
            {
                "hostname": socket.gethostname(),
                "status": "FAIL" if is_error else "PASS",
                "version": self._parse_version_info(),
                **healthchecks,
            },
            status=500 if is_error else 200,
            json_dumps_params={
                # Dump out as JSON with no starting spaces for easier
                # parsability by systems that don't understand JSON.
                "indent": 0
            }
        )

    def _parse_version_info(self):
        try:
            path = os.path.join(settings.BASE_DIR, "version")
            with open(path, "r") as fh:
                return fh.read()
        except FileNotFoundError:
            return "dev"

    def _get_health_db(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM django_migrations")
                cursor.fetchone()
            return "PASS"
        except Exception:
            LOGGER.exception("Database healthcheck failed")
            return "FAIL"


class DebugHttpView(LoginNotRequiredMixin, View):
    """
    Dumps as much of the raw request out as possible. Requires you to be
    signed in as a superuser since the output may be sensitive
    """

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # Let superusers use the form easily, but also allow tokens
        # to access since sometimes it's annoying to sign in. See
        # the `./manage.py create_debug_http_token` command
        if not request.user.is_superuser:
            if "token" in request.GET:
                signer = TimestampSigner(salt="DebugHttpView")
                # If you know this much about the system start being
                # more helpful rather than returning 404
                try:
                    signer.unsign(request.GET["token"], max_age=24*3600)
                except SignatureExpired:
                    return HttpResponse(
                        "Signature expired",
                        status=400,
                        content_type="text/plain; charset=utf-8"
                    )
                except BadSignature:
                    return HttpResponse(
                        "Invalid signature",
                        status=400,
                        content_type="text/plain; charset=utf-8"
                    )
            else:
                raise Http404

        # Django strips the HTTP_ prefix off these and manipulates
        # the values. So they may not actually reflect what was
        # passed in
        extra_headers = ("CONTENT_LENGTH", "CONTENT_TYPE")
        header_pairs = [
            (header, value)
            for header, value in request.META.items()
            if header.startswith("HTTP") or header in extra_headers
        ]

        headers = ""
        for header, value in header_pairs:
            if header.startswith("HTTP_"):
                clean_header = header[5:]
            else:
                clean_header = header

            header = "-".join(
                [h.capitalize() for h in clean_header.lower().split("_")]
            )
            headers += "{}: {}\n".format(header, value)

        msg = (
            "{method} {path} HTTP/1.1\n"
            "{headers}\n\n"
            "{body}"
        ).format(
            method=request.method,
            path=request.get_full_path(),
            headers=headers,
            body=request.body,
        )

        return HttpResponse(
            msg,
            content_type="text/plain; charset=utf-8"
        )


@method_decorator(csrf_exempt, name="dispatch")
class CspReportView(LoginNotRequiredMixin, View):
    """
    Logs Content-Security-Policy violation reports.
    """

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        # Truncate request to stop people abusing the endpoint with huge piles
        # of content. Could make the JSON data invalid or slice a multibyte
        # character.
        content = request.body.decode("utf8")[:1024]
        # Also log the most likely culprit: the browser they're using
        useragent = request.META.get("HTTP_USER_AGENT")[:1024]
        logger = logging.getLogger("frontend")
        logger.warning("CSP Violation Report: %s || %s", content, useragent)

        # No content response
        return HttpResponse(status=204)


@method_decorator(csrf_exempt, name="dispatch")
class JsErrorReportView(LoginNotRequiredMixin, View):
    """
    Logs Javascript error reports from the frontend
    """

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        # Truncate request to stop people abusing the endpoint with huge piles
        # of content. Could make the JSON data invalid or slice a multibyte
        # character.
        content = request.body.decode("utf8")[:1024]
        # Browser they're using might be useful
        useragent = request.META.get("HTTP_USER_AGENT")[:1024]
        logger = logging.getLogger("frontend")
        logger.warning("JS Error: %s || %s", content, useragent)

        # No content response
        return HttpResponse(status=204)
