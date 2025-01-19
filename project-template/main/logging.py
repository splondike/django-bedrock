import collections
import hashlib
import json
import logging
import os
import traceback
from typing import Optional

from django.conf import settings
from django.utils import timezone

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


def get_request_id(request):
    return request.META.get("HTTP_X_REQUEST_ID", "unk")


class RequestContextFilter(logging.Filter):
    """
    Inject HTTP request path and IP information into the LogRecord
    """

    def filter(self, record):
        maybe_request = current_request()
        if not maybe_request:
            record.ip_token = "." * 8
            record.ip_address = "0.0.0.0"
            record.session_id_hash = "." * 8
            record.request_principal = "unk"
            record.request_id = "." * 8
            return True

        maybe_ip = get_request_ip(maybe_request)
        if maybe_ip:
            record.ip_address = maybe_ip
        else:
            record.ip_address = "0.0.0.0"

        if maybe_request.session.session_key:
            record.session_id_hash = hashlib.sha256(maybe_request.session.session_key.encode()).hexdigest()[:8]
        else:
            record.session_id_hash = "." * 8

        if hasattr(maybe_request, "user"):
            record.request_principal = maybe_request.user.principal_logging_identifier()
        else:
            record.request_principal = "anon"

        record.request_id = get_request_id(maybe_request)

        return True


class JsonFormatter:
    def __init__(self, fields, *args, **kwargs):
        self.fields = [
            (key, val)
            for piece in fields.split(" ")
            for (key, val) in (piece.split(":"),)
        ]

    def format(self, record):
        rtn = collections.OrderedDict()
        for key, field in self.fields:
            if field == "time":
                val = timezone.now().isoformat()
            elif field == "app":
                val = "django"
            elif field == "project":
                val = os.environ.get("PROJECT_NAME", "bedrock")
            elif field == "message":
                val = record.getMessage()
            elif field == "exc_info":
                val = getattr(record, field, None)
                if val is not None:
                    val = "".join(traceback.format_exception(val[0], value=val[1], tb=val[2]))
            else:
                val = getattr(record, field, None)
            rtn[key] = val
        return json.dumps(rtn)
