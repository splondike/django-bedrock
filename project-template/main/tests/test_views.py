from main.tests.factories import UserFactory, USER_PASSWORD
from main.tests.base import StandardClientTestCase


class TestLogin(StandardClientTestCase):
    def test_can_login(self):
        # Given a user

        # When we attempt to login to the admin portal as that user
        response = self.client.post(
            "/accounts/login/",
            {
                "username": self.user.email,
                "password": USER_PASSWORD,
                "next": "/"
            }
        )

        # Then the attempt is successful
        print(response.content)
        assert response.status_code == 302
        assert response.url == "/"

    def setup_method(self, method):
        super().setup_method(method)
        self.user = UserFactory()
