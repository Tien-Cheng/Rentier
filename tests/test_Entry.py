from application.models import Entry
from datetime import datetime as dt
import pytest


# Unit Tests


##### Entry Class #####
## Validity Testing -> Check that valid inputs can go in
### Validation is done within the Entry class
@pytest.mark.parametrize(
    "entrylist",
    [
        [
            1,  # User_id (this unit test does not check fk constraints, so user with id 1 does not yet need to exist)
            2,  # Beds
            1,  # Bathrooms
            2,  # Accomodates
            7,  # Minimum Nights
            "Private room",  # Room type
            "Ang Mo Kio",  # Neighborhood
            True,  # Wifi
            True,  # Elevator
            False,  # Pool
            None,  # Actual Price --> Optional Params
            None,  # Link --> Optional Params
            94,  # Prediction
            None, # Difference
        ],
        [
            1,
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
            80 - 70.83 # Difference
        ],
    ],
)
def test_EntryClass(entrylist, capsys):
    with capsys.disabled():
        print(entrylist)
        created = dt.utcnow()

        new_entry = Entry(
            user_id=entrylist[0],
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
            difference=entrylist[13],
            created=created,
        )

        # Assert statements
        assert new_entry.user_id == entrylist[0]
        assert new_entry.beds == entrylist[1]
        assert new_entry.bathrooms == entrylist[2]
        assert new_entry.accomodates == entrylist[3]
        assert new_entry.minimum_nights == entrylist[4]
        assert new_entry.room_type == entrylist[5]
        assert new_entry.neighborhood == entrylist[6]
        assert new_entry.wifi == entrylist[7]
        assert new_entry.elevator == entrylist[8]
        assert new_entry.pool == entrylist[9]
        assert new_entry.actual_price == entrylist[10]
        assert new_entry.link == entrylist[11]
        assert new_entry.prediction == entrylist[12]
        assert new_entry.difference == entrylist[13]
        assert new_entry.created == created


## Expected Failure
"""
1. User does not exist
2. Wrong data type
3. Out of range input
"""


@pytest.mark.xfail(reason="Invalid Data Type", strict=True)
@pytest.mark.parametrize(
    "entrylist",
    [
        [
            1,
            1.5,  # Float data type should be invalid
            1,
            1,
            5,
            "Shared room",
            "Bukit Timah",
            True,
            True,
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            "1.5",  # Cannot be string
            1,
            1,
            5,
            "Shared room",
            "Bukit Timah",
            True,
            True,
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            "1",  # Cannot be string
            1,
            5,
            "Shared room",
            "Bukit Timah",
            True,
            True,
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1.5j,  # Must be int
            5,
            "Shared room",
            "Bukit Timah",
            True,
            True,
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5j,  # Must be int
            "Shared room",
            "Bukit Timah",
            True,
            True,
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5,
            3,  # Invalid room type
            "Bukit Timah",
            True,
            True,
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5,
            "Shared room",
            None,  # Invalid neighborhood
            True,
            True,
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5,
            "Shared room",
            "Bukit Timah",
            1,  # Invalid data type
            True,
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5,
            "Shared room",
            "Bukit Timah",
            True,
            0,  # Invalid data type
            False,
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5,
            "Shared room",
            "Bukit Timah",
            True,
            True,
            1,  # Invalid data type
            None,
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5,
            "Shared room",
            "Bukit Timah",
            True,
            True,
            False,
            "70",  # Must be None or Float
            None,
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5,
            "Shared room",
            "Bukit Timah",
            True,
            True,
            False,
            None,
            54,  # Must be string or None
            70,
            None
        ],
        [
            1,
            1.5,
            1,
            1,
            5,
            "Shared room",
            "Bukit Timah",
            True,
            True,
            False,
            None,
            None,
            None,  # Cannot be None
            None
        ],
    ],
)
def test_EntryValidation_InvalidDataType(entrylist, capsys):
    test_EntryClass(entrylist, capsys)

    # Below lines no longer needed due to built in validty test in class
    # with capsys.disabled():
    #     assert type(entrylist[0]) is int, "User ID should be an integer"
    #     assert type(entrylist[1]) is int, "Data type of beds should be a int"
    #     assert type(entrylist[2]) in {float, int}, "Bathrooms should be an int or float"
    #     assert type(entrylist[3]) is int, "Accomodates should be an int"
    #     assert type(entrylist[4]) is int, "Minimum nights should be an int"
    #     assert type(entrylist[5]) is str, "Room type should be a string"
    #     assert type(entrylist[6]) is str, "Neighborhood should be a string"
    #     assert type(entrylist[7]) is bool, "Wifi should be a bool"
    #     assert type(entrylist[8]) is bool, "Elevator should be a bool"
    #     assert type(entrylist[9]) is bool, "Pool should be a bool"
    #     assert type(entrylist[10]) in {
    #         float,
    #         int,
    #         type(None),
    #     }, "Actual price should be a float, int or None"
    #     assert type(entrylist[11]) in {type(None), str}, "Link should be a str or None"
    #     assert type(entrylist[12]) is float, "Prediction should be a float"


@pytest.mark.xfail(reason="Inputs out of range", strict=True)
@pytest.mark.parametrize(
    "entrylist",
    [
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
                80 - 70.83
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
                80 - 70.83
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
                80 - 70.83
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
                80 - 70.83
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
                80 - 70.83
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
                80 - 70.83
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
                80 - 70.83
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
                100,
                "https://www.airbnb.com/rooms/71896",
                -431,  # Predicted price cannot be negative
                100 + 431
            ],
        ]
    ],
)
def test_EntryValidation_RangeTest(entrylist, capsys):
    test_EntryClass(entrylist, capsys)


@pytest.mark.xfail(reason="Missing inputs", strict=True)
@pytest.mark.parametrize(
    "entrylist",
    [
        [],
        [
            1,
            2,
            5,
            1,
            90,
            "Private room",
            "Bukit Timah",
            True,
            True,
            100,
            "https://www.airbnb.com/rooms/71896",
            431,
            100 - 431
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
            100,
            "https://www.airbnb.com/rooms/71896",
            None,  # cannot be None (missing)
            None
        ],
    ],
)
def test_EntryValidationMissing(entrylist, capsys):
    test_EntryClass(entrylist, capsys)

