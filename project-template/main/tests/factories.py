import factory
from django.contrib.auth import get_user_model


User = get_user_model()
USER_PASSWORD = "password"


class UserFactory(factory.django.DjangoModelFactory):
    """Make a user."""

    email = "user@example.com"
    username = factory.LazyAttribute(lambda obj: obj.email)
    password = factory.PostGenerationMethodCall(
        "set_password",
        USER_PASSWORD
    )
    first_name = "Joe"
    last_name = "User"

    class Meta:
        model = User
        django_get_or_create = ("username",)


class SuperuserFactory(UserFactory):
    first_name = "Jane"
    last_name = "Admin"
    email = "admin@example.com"
    is_superuser = True
    is_staff = True
