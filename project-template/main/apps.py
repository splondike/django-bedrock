from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = "main"

    def ready(self):
        import main.auth.checks  # noqa: F401
        # Ensure the signals are hooked up
        import main.signals  # noqa: E262, F401, E402
