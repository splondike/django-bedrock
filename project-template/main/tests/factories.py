import factory
from django.contrib.auth import get_user_model


User = get_user_model()
USER_PASSWORD = "password"


class UserFactory(factory.django.DjangoModelFactory):
    """Make a user."""

    email = "user@example.com"
    password = factory.PostGenerationMethodCall(
        "set_password",
        USER_PASSWORD
    )

    class Meta:
        model = User
        django_get_or_create = ("email",)
