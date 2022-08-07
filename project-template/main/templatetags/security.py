from django import template
from django.utils.safestring import mark_safe


register = template.Library()  # pylint: disable=invalid-name


@register.simple_tag(takes_context=True)
def content_security_policy_nonce(context):
    """
    Returns the Content-Security-Policy nonce which can be used to tag
    an inline script as safe.

    Usage:

        <script {% content_security_policy_nonce %}>

    @see hmif.middleware.ContentSecurityPolicyMiddleware
    """
    request = context.get("request")

    if request and hasattr(request, "_csp_nonce"):
        val = request._csp_nonce  # pylint:disable=protected-access
        return mark_safe(f"nonce=\"{val}\"")
    else:
        return None
