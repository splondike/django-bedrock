import json

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


class TestJsonApi(StandardClientTestCase):
    def test_success_response(self):
        # When we post some valid JSON to our endpiont
        response = self.client.post(
            "/demoapi/foo",
            json.dumps({
                "data": {
                    "attributes": {
                        "body_field": "2025-02-08 13:16:00"
                    }
                }
            }),
            headers={
                "my_header": "foo",
            },
            content_type="application/json"
        )

        print(response.content)
        assert response.status_code == 200

    def test_validation_error_response(self):
        # When we post some valid JSON to our endpiont
        response = self.client.post(
            "/demoapi/foo",
            json.dumps({
                "data": {
                    "attributes": {
                        "body_field": "nottimestamp"
                    }
                }
            }),
            content_type="application/json"
        )

        print(response.content)
        assert response.status_code == 400
        assert b"valid date" in response.content
