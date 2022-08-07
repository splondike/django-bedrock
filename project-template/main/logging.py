from typing import Optional
import logging
import ipaddress
import base64
import binascii
import secrets

from django.conf import settings

from main.threadlocals import current_request


def get_request_ip(request) -> Optional[str]:
    if settings.USE_X_FORWARDED_FOR:
        header = request.META.get('HTTP_X_FORWARDED_FOR')
        if header is None:
            return None

        # Nginx appends the request IP to X-Forwarded-For,
        # not prepend like other proxies
        return header.split(',')[-1].strip()
    else:
        return request.META["REMOTE_ADDR"]


class RequestContextFilter(logging.Filter):
    """
    Inject HTTP request path and IP information into the LogRecord
    """

    def filter(self, record):
        maybe_request = current_request()
        if not maybe_request:
            record.ip_token = "." * 8
            record.ip_address = "0.0.0.0"
            record.session_token = "." * 8
            record.trace_id = "." * 8
            return True

        maybe_ip = get_request_ip(maybe_request)
        if maybe_ip:
            ip_bin = ipaddress.ip_address(maybe_ip).packed
            record.ip_address = maybe_ip
            # ip_token is a shorter and fixed length encoding of the IP
            record.ip_token = binascii.hexlify(ip_bin).decode()
        else:
            record.ip_token = "." * 8
            record.ip_address = "0.0.0.0"

        if maybe_request.session.session_key:
            record.session_token = maybe_request.session.session_key[:8]
        else:
            record.session_token = "." * 8

        # Random id for finding all log messages for a given request
        record.trace_id = base64.b32encode(secrets.token_bytes(5)).decode()

        return True
