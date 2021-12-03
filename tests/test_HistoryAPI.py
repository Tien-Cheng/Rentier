import pytest
import json
from application import app

# Add Entry

# Test that adding normal entries to history works correctly
@pytest.mark.usefixtures("populate_users")
@pytest.mark.parametrize(
    "entrylist",
    [
        [
            2,  # User ID
            3,  # Beds
            1,  # Bathrooms
            6,  # Accomodates
            90,  # Minimum Nights
            "Private room",  # Room type
            "Tampines",  # Neighborhood
            True,  # Wifi
            False,  # Elevator
            False,  # Pool
            178,  # Actual price
            "https://www.airbnb.com/rooms/71609",  # Link to listing
            155.06,  # Predicted
        ],
        [
            1,  # User ID
            2,  # Beds
            1,  # Bathrooms
            3,  # Accomodates
            90,  # Minimum Nights
            "Shared room",  # Room type
            "Marine Parade",  # Neighborhood
            True,  # Wifi
            True,  # Elevator
            False,  # Pool
            None,  # Actual price
            None,  # Link to listing
            95.09,  # Predicted
        ], # TODO: Add more test cases
    ],
)
def test_add_entry(client, entrylist, capsys):
    with capsys.disabled():
        data = dict(
            beds=entrylist[1],
            bathrooms=entrylist[2],
            accomodates=entrylist[3],
            minimum_nights=entrylist[4],
            room_type=entrylist[5],
            neighborhood=entrylist[6],
            wifi=entrylist[7],
            elevator=entrylist[8],
            pool=entrylist[9],
            actual_price=entrylist[10],
            link=entrylist[11],
            prediction=entrylist[12],
        )

        response = client.post(
            f"/api/history/{entrylist[0]}",
            data=json.dumps(data),
            content_type="application/json",
        )
        response_body = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        assert response_body["result"]


# Test that adding entries with invalid user_id results in failure
@pytest.mark.skipif(
    app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"),
    reason="SQLite does not enforce foreign key constraints",
)
@pytest.mark.usefixtures("populate_users")
@pytest.mark.xfail(reason="User ID does not exist", strict=True)
@pytest.mark.parametrize(
    "entrylist",
    [
        [
            -1,  # User_id
            2,  # Beds
            1,  # Bathrooms
            2,  # Accomodates
            7,  # Minimum Nights
            "Private room",  # Room type
            "Ang Mo Kio",  # Neighborhood
            True,  # Wifi
            True,  # Elevator
            False,  # Pool
            None,  # Actual Price
            None,  # Link
            94.0,  # Prediction
        ],
        [
            545,
            1,
            1,
            2,
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            80,
            "https://www.airbnb.com/rooms/71896",
            70.83,
        ],
    ],
)
def test_add_entry_invalid_user_id(client, entrylist, capsys):
    test_add_entry(client, entrylist, capsys)


# Tests on validity of data are conducted in test_Entry.py, so will not duplicate here


# Get History
@pytest.mark.parametrize(
    "user_history",
    [
        {
            "user_id": 2,
            "history": [
                {
                    "beds": 3,
                    "bathrooms": 1,
                    "accomodates": 6,
                    "minimum_nights": 90,
                    "room_type": "Private room",
                    "neighborhood": "Tampines",
                    "wifi": True,
                    "elevator": False,
                    "pool": False,
                    "actual_price": 178,
                    "link": "https://www.airbnb.com/rooms/71609",
                    "prediction": 155.06,
                }
            ],
        },
        {
            "user_id": 1,
            "history": [
                {
                    "beds": 2,
                    "bathrooms": 1,
                    "accomodates": 3,
                    "minimum_nights": 90,
                    "room_type": "Shared room",
                    "neighborhood": "Marine Parade",
                    "wifi": True,
                    "elevator": True,
                    "pool": False,
                    "actual_price": None,
                    "link": None,
                    "prediction": 95.09,
                }
            ],
        },
    ],
)
def test_get_user_history(client, user_history, capsys):
    with capsys.disabled():
        user_id = user_history["user_id"]
        response = client.get(f"/api/history/{user_id}")
        response_body = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        for entry, expected in zip(response_body, user_history["history"]):
            for key in (
                "beds",
                "bathrooms",
                "accomodates",
                "minimum_nights",
                "room_type",
                "neighborhood",
                "wifi",
                "elevator",
                "pool",
                "actual_price",
                "link",
                "prediction",
            ):
                assert entry[key] == expected[key]


# Remove Entry
@pytest.mark.parametrize("entry_ids", [
    {
        "user_id" : 1,
        "id" : 2
    },
    {
        "user_id" : 2,
        "id" : 1
    }
])
def test_delete_entry(client, entry_ids, capsys):
    with capsys.disabled():
        user_id = entry_ids["user_id"]
        entry_id = entry_ids["id"]
        response = client.delete(f"/api/history/{user_id}/{entry_id}/")
        response_body = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

        assert response_body["result"] == entry_id


## Expected Failure: Deleting an entry not related to the user
@pytest.mark.xfail(reason="Entry does not belong to the user", strict=True)
@pytest.mark.parametrize("entry_ids", [
    {
        "user_id" : 1,
        "id" : 2
    },
    {
        "user_id" : 2,
        "id" : 1
    }
])
def test_delete_entry_unauthorized(client, entry_ids, capsys):
    raise NotImplementedError