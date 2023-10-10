import pytest

from wtforms.validators import AnyOf
from wtforms.validators import ValidationError


@pytest.mark.parametrize("test_v, test_list", [("b", ["a", "b", "c"]), (2, [1, 2, 3])])
def test_anyof_passes(test_v, test_list, dummy_form, dummy_field):
    """
    it should pass if the test_v is present in the test_list
    """
    validator = AnyOf(test_list)
    dummy_field.data = test_v
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize("test_v, test_list", [("d", ["a", "b", "c"]), (6, [1, 2, 3])])
def test_anyof_raisses(test_v, test_list, dummy_form, dummy_field):
    """
    it should raise ValueError if the test_v is not present in the test_list
    """
    validator = AnyOf(test_list)
    dummy_field.data = test_v
    with pytest.raises(ValueError):
        validator(dummy_form, dummy_field)


def test_any_of_values_formatter(dummy_form, dummy_field):
    """
    Test AnyOf values_formatter formating of error message
    """

    def formatter(values):
        return "::".join(str(x) for x in reversed(values))

    validator = AnyOf([7, 8, 9], message="test %(values)s", values_formatter=formatter)
    dummy_field.data = 4
    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)

    assert str(e.value) == "test 9::8::7"


def test_none_multiple_values(dummy_form, dummy_field):
    """
    the validator should work with multiple values like produced
    by SelectMultiple fields
    """
    dummy_field.data = ["a", "e"]
    validator = AnyOf(["a", "b", "c"])
    validator(dummy_form, dummy_field)

    dummy_field.data = ["d", "e"]
    validator = AnyOf(["a", "b", "c"])
    with pytest.raises(ValueError):
        validator(dummy_form, dummy_field)
