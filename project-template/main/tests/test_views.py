from main.tests.factories import SuperuserFactory, USER_PASSWORD
from main.tests.base import StandardClientTestCase


class TestAdminLogin(StandardClientTestCase):
    def test_can_login(self):
        # Given a superuser

        # When we attempt to login to the admin portal as that user
        response = self.client.post(
            "/admin/login/",
            {
                "username": self.user.username,
                "password": USER_PASSWORD,
                "next": "/admin/"
            }
        )

        # Then the attempt is successful
        print(response.content)
        assert response.status_code == 302
        assert response.url == "/admin/"

    def setup_method(self, method):
        super().setup_method(method)
        self.user = SuperuserFactory()
