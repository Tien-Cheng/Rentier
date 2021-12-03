import pytest
from datetime import datetime as dt
from flask import json, session


@pytest.mark.parametrize(
    "userlist",
    [
        ["email1@gmail.com", "Password1234!@#$"],
        ["email2@gmai.com", "Password1234!@#$"],
    ],
)
def test_user_add_api(client, userlist, capsys):
    with capsys.disabled():
        # Prepare data into dictionary
        data = {"email": userlist[0], "password": userlist[1]}

        # Send a post request to the api
        response = client.post(
            "/api/users/", data=json.dumps(data), content_type="application/json"
        )
        response_body = json.loads(response.get_data(as_text=True))

        # Check response status code
        assert response.status_code == 200
        # Check consistent content type
        assert response.headers["Content-Type"] == "application/json"

        # Check result is consistent with what was sent
        assert response_body["id"], "User ID was not returned!"
        assert (
            response_body["email"] == userlist[0]
        ), "Returned email does not match up!"
        assert response_body["password_hash"], "Password hash was not returned!"
        assert response_body["created"], "Created date was not returned!"

        # Check that created date makes sense
        date = dt.strptime(response_body["created"], "%a, %d %b %Y %H:%M:%S %Z")
        assert (
            dt.utcnow() - date
        ).total_seconds() < 5 * 60, "Created date is too far off to be correct"

        # TODO: Decide if I should check the database for the user


@pytest.mark.usefixtures("populate_users")
@pytest.mark.xfail(reason="Duplicate email in database", strict=True)
@pytest.mark.parametrize(
    "userlist",
    [
        [
            ["user_1@example.com", "Password1234!"],
            ["user_2@example.com", "Password567890!"],
        ]
    ],
)
def test_user_add_api_duplicate_email(client, userlist, capsys):
    with capsys.disabled():
        # Prepare data into dictionary
        data = {"email": userlist[0], "password": userlist[1]}

        # Send a post request to the api
        response = client.post(
            "/api/users", data=json.dumps(data), content_type="application/json"
        )
        # response_body = json.loads(response.get_data(as_text=True))

        # Check that it failed
        # assert response.status_code == 400


@pytest.mark.usefixtures("populate_users")
@pytest.mark.parametrize(
    "userlist",
    [
        ["user_1@example.com", "Password1234!", True],
        ["user_2@example.com", "Password567890!", False],
    ],
)
def test_user_login_api(client, userlist, capsys):
    with capsys.disabled():
        with client:
            data = {
                "email": userlist[0],
                "password": userlist[1],
                "remember_me": userlist[2],
            }

            response = client.post(
                "/api/login", data=json.dumps(data), content_type="application/json"
            )
            response_body = json.loads(response.get_data(as_text=True))

            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            assert response_body["email"] == userlist[0]
            assert response_body["password"] == userlist[1]
            assert response_body["remember_me"] == userlist[2]
            assert session.permanent == response_body["remember_me"]
            assert session["user_id"] == response_body["id"]


@pytest.mark.usefixtures("fake_login")
@pytest.mark.parametrize("fake_login", [1], indirect=True)
def test_user_logout(client, capsys):
    with capsys.disabled():
        with client:
            response = client.post("/logout")
            assert response.status_code == 302
            assert "user_id" not in session, "Not logged out!"
