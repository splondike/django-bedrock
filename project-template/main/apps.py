from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = "main"

    def ready(self):
        import main.auth.checks  # noqa: F401
