from main.auth.base import AuthenticationPrincipal


class UserPrincipal(AuthenticationPrincipal):
    """
    Authorization logic for a user from the database.
    """

    def has_perm(self, perm, obj):
        return True

    def principal_logging_identifier(self):
        return f"user:{self.pk}"


class APITokenPrincipal(AuthenticationPrincipal):
    """
    Authorization logic for a user from an API token.
    """

    def principal_logging_identifier(self):
        return f"apitoken:{self.pk}"


class AnonymousPrincipal(AuthenticationPrincipal):
    """
    An anonymous auth principal. Similar to Django's AnonymousUser
    """

    @property
    def is_anonymous(self):
        return True

    @property
    def is_authenticated(self):
        return False

    def principal_logging_identifier(self):
        return "anonymous"
