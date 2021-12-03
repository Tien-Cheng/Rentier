# Testing for Rentier

## `test_Entry.py`
This script tests the `Entry` class of the app. The Entry class consists of entries to a User's history
### Range Testing
- Test that valid inputs are accepted

### Expected Failure Testing
- Tests that entries with wrong data types, out of range inputs and missing inputs are rejected

## `test_User.py`
This script tests the `User` class of the app. The User class consists of users registered with the app.

### Range Testing
- Check that users with valid email and password can be inserted into the database

### Expected Failure Testing
- Check that users with invalid email or missing essential info cannot be inserted into the database.

## `test_UserManagementAPI.py`
This script tests the APIs for user management. Namely, the registration, login and logout functionality.

### Range Testing
- Check that users can be registered if their email and password are valid, with no duplicates
- Check that users can be logged in if their credentials are valid
- Check that users can be logged out once logged in
### Expected Failure Testing
- Check that duplicate emails are not accepted
- Check that users fail to login if their credentials are invalid

## `test_PredictionAPI.py`
This script tests the APIs for prediction. 

### Validity Testing
- Check that examples in the training set can be predicted with low error by the model

### Consistency Testing
- Check that swapping features in the inputs to the model causes inconsistency in the results

### Expected Failure Testing
- Check that out of range inputs are rejected

## `test_HistoryAPI.py`
This script tests the APIs for user history

### Range Testing
- Check that adding normal entries to user history works correctly
- Check that users can delete entries from their history
### Consistency Testing
- Check that uses can only access their own history
### Expected Failure Testing
- Check that users cannot add entries to other users history
- Check that users cannot delete entries from other peoples history

## `test_Routes.py`
### Range Testing
- Check that users that are logged in can access restricted routes (for non users)
### Unexpected Failure Testing
- Check that accessing invalid endpoints (no permission or does not exist or wrong methiod) gives an appropriate error
