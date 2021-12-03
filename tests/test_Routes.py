import pytest
import json


@pytest.mark.parametrize(
    "endpoint",
    [
        ("invalid_link", 404),
        ("history", 303),
        ("", 200),
        ("login", 200),
        ("register", 200),
        ("predict", 303),  # Trying to access page when not logged in
    ],
)
def test_Route(client, endpoint, capsys):
    """Unexpected failure from trying to access endpoints"""
    with capsys.disabled():
        endpoint, code = endpoint[0], endpoint[1]
        response = client.get(f"/{endpoint}")
        assert response.status_code == code


@pytest.mark.parametrize("endpoint", [("history", 200), ("predict", 200)])
@pytest.mark.usefixtures("fake_login")
def test_Route_Authorized(client, endpoint, capsys):
    test_Route(client, endpoint, capsys)
    with client.session_transaction() as sess:
        sess.pop("user_id", None)  # logout

@pytest.mark.parametrize("endpoint", [
    ("api/history/1")
])