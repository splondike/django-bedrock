"""
Makes request available as a global object.

This should probably just be used for enrichment of log messages.
"""

from threading import local


thread_local_storage = local()


def current_request():
    """
    Returns the currently active request (or None if we're
    outside a request context)
    """

    return getattr(thread_local_storage, "request", None)


class ThreadLocalMiddleware:
    """
    Simple middleware that adds the request object in thread local storage.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        thread_local_storage.request = request

        try:
            return self.get_response(request)
        finally:
            # Clear storage after processing the request because
            # threads might be reused for multiple requests. We
            # wouldn't want to associate previous info with the
            # next request by accident.
            if hasattr(thread_local_storage, "request"):
                del thread_local_storage.request
