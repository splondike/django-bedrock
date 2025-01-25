import secrets
import random
from collections import OrderedDict

from django.conf import settings
from django.urls import reverse
from django.utils.cache import add_never_cache_headers


class ContentSecurityPolicyMiddleware:
    """
    Adds a Content-Security-Policy header to the application. Since we're using
    Whitenoise this should be added to all app assets.

    Does a couple more things also:
    * Add a _csp_nonce variable to the request for tagging any inline scripts.
    * Probabilistically add a report_uri to the CSP which uses the csp_report
      URL to log info to the normal logging system.

    @see https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
    @see hmif/templatetags/hmif.py#content_security_policy_nonce
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request._csp_nonce = self._generate_nonce()

        response = self.get_response(request)

        setting_status = settings.CONTENT_SECURITY_POLICY_ACTIVE
        if setting_status != "disabled":
            if setting_status == "active":
                header_name = "Content-Security-Policy"
            elif setting_status == "report_only":
                header_name = "Content-Security-Policy-Report-Only"
            else:
                raise AssertionError(
                    "Misconfigured CONTENT_SECURITY_POLICY_ACTIVE, "
                    f"got {setting_status}"
                )
            response[header_name] = self._build_policy(
                request._csp_nonce,
                request.path.startswith("/admin/")
            )

        return response

    def _build_policy(self, nonce, is_admin):
        # Can check for issues with https://csp-evaluator.withgoogle.com/
        policies = OrderedDict({
            "default-src": ["'self'"],
            "img-src": ["'self'", "data:", "blob:"],
            "style-src": ["'self'", "'unsafe-inline'"],
            # Only allow nonce, so people can't find a random script on our
            # server and XSS include that. unsafe-inline will be ignored by
            # newer browsers, but will allow older browsers to operate under
            # a less secure regime.
            "script-src": ["'unsafe-inline'", f"'nonce-{nonce}'"],
            # No iframes etc
            "object-src": ["'none'"],
            # Block XSS setting the base element to point everything to their
            # domain
            "base-uri": ["'none'"]
        })

        if is_admin:
            # Admin doesn't know about our nonce thing
            policies["script-src"].append("'self'")

        if random.random() < settings.CONTENT_SECURITY_POLICY_REPORT_PROB:
            # Probabilistic to avoid hammering the server if we have a
            # significant CSP issue, but continue to allow sampling.
            policies['report-uri'] = [reverse('csp_report')]

        return "; ".join(
            " ".join([key] + values)
            for key, values in policies.items()
        )

    def _generate_nonce(self):
        return secrets.token_hex(16)


class NoCacheDefaultMiddleware:
    """
    Ensure's we're not caching any of our HTML views by default
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not response.has_header("Cache-Control"):
            # Allow people to set their own headers, but if they don't assume no cache
            add_never_cache_headers(response)
            pass


        return response
