import pytest

from main.api_helpers import extract_json_path

class TestExtractJsonPath:
    @pytest.mark.parametrize("path, obj, expected", [
        ("/foo/bar", {"foo": {"bar": True}}, True),
        ("/foo/0", {"foo": [True]}, True),
        ("/~01", {"~1": True}, True),
        ("/~1", {"/": True}, True),
        ("/0", [True], True),
        ("/", [True], [True]),
    ])
    def test_json_path(self, path, obj, expected):
        actual = extract_json_path(path, obj)
        assert actual == expected


    def test_errors_if_not_found(self):
        with pytest.raises(KeyError):
            extract_json_path("/foo", {})
