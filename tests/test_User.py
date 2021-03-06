from application.models import User
from datetime import datetime as dt
import pytest
from werkzeug.security import generate_password_hash


#### User Management Class ####
@pytest.mark.parametrize(
    "userlist",
    [["user@yahoo.com", "Password1234!@#$"], ["test_user@ichat.com", "fadd$$@!45FF"]],
)
def test_UserClass(userlist, capsys):
    with capsys.disabled():
        created = dt.utcnow()
        password_hash = generate_password_hash(userlist[1])
        new_user = User(
            email=userlist[0],
            password_hash=password_hash,
            created=created,
        )
        # Assert statements
        assert new_user.email == userlist[0]
        assert new_user.password_hash == password_hash
        assert new_user.created == created


## Expected Failure

@pytest.mark.xfail(reason="Invalid email", strict=True)
@pytest.mark.parametrize(
    "userlist",
    [
        ["invalid_email", "Password1234!@#$"],
        # Removed these, as model validation cannot check password, since it is already hashed. 
        # ["valid@email.com", "invalid_password!!!"],  # no numbers
        # ["yeet@ichat.com", "short"],  # too short
        ["sp.edu.sg", "Password1234!@#$"],
        ["hello world", "Password1234!@"],
        # ["valid_2@gmail.com", "Passowrd1234"],  # no symbol
    ],
)
def test_UserClassValidation_invaliddetails(userlist, capsys):
    test_UserClass(userlist, capsys)

@pytest.mark.xfail(reason="Missing inputs", strict=True)
@pytest.mark.parametrize("userlist", [
    [],
    [None, None],
    [None],
    ["email@email.com", None],
    [None, "Password1234!@#$"],
])
def test_UserClassValidation_missing(userlist, capsys):
    test_UserClass(userlist, capsys)


