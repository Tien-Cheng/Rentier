import pytest
import json


@pytest.mark.usefixtures("fake_login")
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
        if len(entrylist) > 9:
            data["actual_price"] = entrylist[9]
        else:
            data["actual_price"] = None
        response = client.post(
            "/api/predict", data=json.dumps(data), content_type="application/json"
        )
        response_body = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        # Check that prediction result is reasonable
        pred = float(response_body["prediction"])
        assert pred > 0, "Predicted value should be greater than 0"
        if data["actual_price"] is not None:
            assert (
                abs(float(response_body["difference"])) < 36
            ), "Prediction value is likely to be invalid"

@pytest.mark.xfail(reason="Input parameters are not consistent")
@pytest.mark.parametrize(
    "entrylist",
    [
        [
            6,
            1.5,
            1, # Swap number of beds with accomodates
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
            81,
            1,
            1, # Swap bathrooms with minimum_nights
            "Private room",
            "Novena",
            True,
            False,
            False,
            115,
            "https://www.airbnb.com/rooms/45149222",
        ],
        [
            1,
            1,
            1,
            81, 
            "Private room",
            "Novena",
            False,
            True, # Swap elevator with wifi
            False,
            115,
            "https://www.airbnb.com/rooms/45149222",
        ],
    ],
)
def test_predict_consistency(client, entrylist, capsys):
    test_predict_api(client, entrylist, capsys)

@pytest.mark.xfail(reason="Inputs out of range", strict=True)
@pytest.mark.usefixtures("fake_login")
@pytest.mark.parametrize(
    "entrylist",
    [
        [
            -2,  # Beds Cannot have negative numbers
            1,
            2,
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            # 80,
            # "https://www.airbnb.com/rooms/71896",  # Test optional
        ],
        [
            2,
            -5,  # Bathrooms Cannot have negative numbers
            2,
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            # 80,
            # "https://www.airbnb.com/rooms/71896",  # Test optional
        ],
        [
            2,
            5,
            0,  # Accomodates cannot be zero
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            # 80,
            # "https://www.airbnb.com/rooms/71896",  # Test optional
        ],
        [
            2,
            5,
            2,
            -42,  # minimum_nights Cannot have negative numbers
            "Private room",
            "Bukit Timah",
            True,
            True,
            True,
            # 80,
            # "https://www.airbnb.com/rooms/71896",  # Test optional
        ],
        [
            2,
            5,
            2,
            90,
            "Filet O Fish",  # Invalid room type
            "Bukit Timah",
            True,
            True,
            True,
            # 80,
            # "https://www.airbnb.com/rooms/71896",  # Test optional
        ],
        [
            2,
            5,
            2,
            90,
            "Private room",
            "Polytechnic",  # Invalid neighborhood
            True,
            True,
            True,
            # 80,
            # "https://www.airbnb.com/rooms/71896",
        ],
    ],
)
def test_predict_api_rangetests(client, entrylist, capsys):
    test_predict_api(
        client, entrylist, capsys
    ) 
