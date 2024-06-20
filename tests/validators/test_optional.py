import pytest

from wtforms.validators import optional
from wtforms.validators import StopValidation


def test_input_optional_passes(dummy_form, dummy_field):
    """
    optional should pause with given values
    """
    validator = optional()
    dummy_field.data = "foobar"
    dummy_field.raw_data = ["foobar"]
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize("data_v, raw_data_v", [("", ""), ("   ", "   "), ("\t", "\t")])
def test_input_optional_raises(data_v, raw_data_v, dummy_form, dummy_field):
    """
    optional should stop the validation chain if the data are not given
    errors should be erased because the value is optional
    white space should be considered as empty string too
    """
    validator = optional()
    dummy_field.data = data_v
    dummy_field.raw_data = raw_data_v

    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)

    assert validator.field_flags == {"optional": True}

    dummy_field.errors = ["Invalid Integer Value"]
    assert len(dummy_field.errors) == 1

    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)

    assert len(dummy_field.errors) == 0


def test_input_optional_raises_with_empty_formdata(dummy_form, dummy_field):
    """
    optional should not stop the validation chain if field.data is not empty
    """
    validator = optional()
    dummy_field.data = "abc"
    dummy_field.raw_data = None

    dummy_field.errors = ["Invalid Integer Value"]
    assert len(dummy_field.errors) == 1

    validator(dummy_form, dummy_field)

    assert len(dummy_field.errors) == 1
