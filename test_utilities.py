import pytest
from utilities import normalize_array, str2bool, average_dictionary
from exceptions import InvalidInputException

# Test array normalization
def test_normalize_array():
    assert normalize_array([2, 2]) == [0.5, 0.5]
    assert normalize_array([0, 0]) == [0, 0]
    assert normalize_array([3, 1]) == [0.75, 0.25]

# Test parsing of input string to boolean
def test_str2bool_valid():
    assert str2bool("True") == True
    assert str2bool("true") == True
    assert str2bool(True) == True
    assert str2bool("False") == False
    assert str2bool("false") == False
    assert str2bool(False) == False

    with pytest.raises(InvalidInputException):
        str2bool("yes")

# Test calculating numerical mean of dictionary values
def test_average_dictionary():
    assert average_dictionary({"a": 2, "b": 4}) == 3.0
    assert average_dictionary({}) == 0
    assert average_dictionary({"x": 5}) == 5.0
