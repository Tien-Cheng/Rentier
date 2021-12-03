import pytest
import json


@pytest.mark.parametrize(
    "entrylist",
    [
        [
            1,
            1.5,
            6,
            1,
            "Entire home/apt",
            "Kallang",
            True,
            True,
            True,
            183,
            "https://www.airbnb.com/rooms/15100514",
        ],
        [
            1,
            1,
            1,
            81,
            "Private room",
            "Novena",
            True,
            False,
            False,
            115,
            "https://www.airbnb.com/rooms/45149222",
        ],
    ],
)
def test_predict_api(client, entrylist, capsys):
    with capsys.disabled():
        data = {
            "beds": entrylist[0],
            "bathrooms": entrylist[1],
            "accomodates": entrylist[2],
            "minimum_nights": entrylist[3],
            "room_type": entrylist[4],
            "neighborhood": entrylist[5],
            "wifi": entrylist[6],
            "elevator": entrylist[7],
            "pool": entrylist[8],
        }

        response = client.post(
            "/api/predict", data=json.dumps(data), content_type="application/json"
        )
        response_body = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        # Check that prediction result is reasonable
        pred = float(response_body["prediction"])
        assert pred > 0, "Predicted value should be greater than 0"
        assert (
            abs(float(entrylist[-2]) - pred) < 36
        ), "Prediction value is likely to be invalid"


@pytest.mark.xfail(reason="Inputs out of range", strict=True)
@pytest.mark.parametrize(
    "entrylist",
    [
        [
            1,
            -2,  # Beds Cannot have negative numbers
            1,
            2,
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            80,
            "https://www.airbnb.com/rooms/71896",  # Test optional
            70.83,
        ],
        [
            1,
            2,
            -5,  # Bathrooms Cannot have negative numbers
            1,
            2,
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            80,
            "https://www.airbnb.com/rooms/71896",  # Test optional
            70.83,
        ],
        [
            1,
            2,
            5,
            0,  # Accomodates cannot be zero
            2,
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            80,
            "https://www.airbnb.com/rooms/71896",  # Test optional
            70.83,
        ],
        [
            1,
            2,
            5,
            1,
            2,
            -42,  # minimum_nights Cannot have negative numbers
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            80,
            "https://www.airbnb.com/rooms/71896",  # Test optional
            70.83,
        ],
        [
            1,
            2,
            5,
            1,
            2,
            90,
            "Filet O Fish",  # Invalid room type
            "Bukit Timah",
            True,
            True,
            True,
            80,
            "https://www.airbnb.com/rooms/71896",  # Test optional
            70.83,
        ],
        [
            1,
            2,
            5,
            1,
            2,
            90,
            "Private room",
            "Polytechnic",  # Invalid neighborhood
            True,
            True,
            True,
            80,
            "https://www.airbnb.com/rooms/71896",
            70.83,
        ],
        [
            1,
            2,
            5,
            1,
            2,
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            -100,  # Actual price cannot be negative
            "https://www.airbnb.com/rooms/71896",
            70.83,
        ],
    ],
)
def test_predict_api_rangetests(client, entrylist, capsys):
    test_predict_api(
        client, entrylist, capsys
    )  # TODO: not working properly rn -> it api_predict needs to validate the input
