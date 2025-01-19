from functools import partial

from django.core.exceptions import BadRequest
from django.contrib.auth.middleware import AuthenticationMiddleware as DjangoAuthenticationMiddleware
from django.utils.functional import SimpleLazyObject

from main.auth.instances import AnonymousPrincipal


def get_token_principal(token_value):
    return AnonymousPrincipal()


async def aget_token_principal(token_value):
    return get_token_principal(token_value)


class AuthenticationMiddleware(DjangoAuthenticationMiddleware):
    def process_request(self, request):
        auth_header_prefix = "Bearer "
        auth_header = request.META.get("Authorization")
        if auth_header is not None:
            if not auth_header.startswith(auth_header_prefix):
                raise BadRequest("Need 'Bearer ' prefix on Authorization header")

            token_value = auth_header[len(auth_header_prefix):]
            request.user = SimpleLazyObject(lambda: get_user(token_value))
            request.auser = partial(aget_token_principal, token_value)
        else:
            super().process_request(request)
