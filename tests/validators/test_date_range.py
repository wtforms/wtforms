from datetime import date
from datetime import datetime

import pytest

from wtforms.validators import DateRange
from wtforms.validators import ValidationError


@pytest.mark.parametrize(
    ("min_v", "max_v", "test_v"),
    (
        (datetime(2023, 5, 23, 18), datetime(2023, 5, 25), date(2023, 5, 24)),
        (date(2023, 5, 24), datetime(2023, 5, 25), datetime(2023, 5, 24, 15)),
        (datetime(2023, 5, 24), None, date(2023, 5, 25)),
        (None, datetime(2023, 5, 25), datetime(2023, 5, 24)),
    ),
)
def test_date_range_passes(min_v, max_v, test_v, dummy_form, dummy_field):
    """
    It should pass if the test_v is between min_v and max_v
    """
    dummy_field.data = test_v
    validator = DateRange(min_v, max_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("min_v", "max_v", "test_v"),
    (
        (date(2023, 5, 24), date(2023, 5, 25), None),
        (datetime(2023, 5, 24, 18, 3), date(2023, 5, 25), None),
        (datetime(2023, 5, 24), datetime(2023, 5, 25), None),
        (datetime(2023, 5, 24), datetime(2023, 5, 25), datetime(2023, 5, 20)),
        (datetime(2023, 5, 24), datetime(2023, 5, 25), datetime(2023, 5, 26)),
        (datetime(2023, 5, 24), None, datetime(2023, 5, 23)),
        (None, datetime(2023, 5, 25), datetime(2023, 5, 26)),
    ),
)
def test_date_range_raises(min_v, max_v, test_v, dummy_form, dummy_field):
    """
    It should raise ValidationError if the test_v is not between min_v and max_v
    """
    dummy_field.data = test_v
    validator = DateRange(min_v, max_v)
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("min_v", "max_v", "min_flag", "max_flag"),
    (
        (datetime(2023, 5, 24), datetime(2023, 5, 25), "2023-05-24", "2023-05-25"),
        (None, datetime(2023, 5, 25), None, "2023-05-25"),
        (datetime(2023, 5, 24), None, "2023-05-24", None),
    ),
)
def test_date_range_field_flags_are_set_date(min_v, max_v, min_flag, max_flag):
    """
    It should format the min and max attribute as yyyy-mm-dd
    when input_type is ``date`` (default)
    """
    validator = DateRange(min_v, max_v)
    assert validator.field_flags.get("min") == min_flag
    assert validator.field_flags.get("max") == max_flag


@pytest.mark.parametrize(
    ("min_v", "max_v", "min_flag", "max_flag"),
    (
        (date(2023, 5, 24), date(2023, 5, 25), "2023-05-24T00:00", "2023-05-25T00:00"),
        (None, date(2023, 5, 25), None, "2023-05-25T00:00"),
        (date(2023, 5, 24), None, "2023-05-24T00:00", None),
    ),
)
def test_date_range_field_flags_are_set_datetime(min_v, max_v, min_flag, max_flag):
    """
    It should format the min and max attribute as YYYY-MM-DDThh:mm
    when input_type is ``datetime-local`` (default)
    """
    validator = DateRange(min_v, max_v, input_type="datetime-local")
    assert validator.field_flags.get("min") == min_flag
    assert validator.field_flags.get("max") == max_flag


def test_date_range_input_type_invalid():
    """
    It should raise if the input_type is not either datetime-local or date
    """
    with pytest.raises(ValueError) as exc_info:
        DateRange(input_type="foo")

    (err_msg,) = exc_info.value.args
    assert err_msg == "Only datetime-local or date are allowed, not 'foo'"


def _dt_callback_min():
    return datetime(2023, 5, 24, 15, 3)


def _d_callback_min():
    return date(2023, 5, 24)


def _dt_callback_max():
    return datetime(2023, 5, 25, 0, 3)


def _d_callback_max():
    return date(2023, 5, 25)


@pytest.mark.parametrize(
    ("min_v", "max_v", "test_v"),
    (
        (_dt_callback_min, _dt_callback_max, datetime(2023, 5, 24, 15, 4)),
        (_d_callback_min, _d_callback_max, datetime(2023, 5, 24, 15, 4)),
        (_dt_callback_min, None, datetime(2023, 5, 24, 15, 4)),
        (None, _dt_callback_max, datetime(2023, 5, 24, 15, 2)),
        (None, _dt_callback_max, date(2023, 5, 24)),
    ),
)
def test_date_range_passes_with_callback(min_v, max_v, test_v, dummy_form, dummy_field):
    """
    It should pass with a callback set as either min or max
    """
    dummy_field.data = test_v
    validator = DateRange(min_callback=min_v, max_callback=max_v)
    validator(dummy_form, dummy_field)


def test_date_range_min_callback_and_value_set():
    """
    It should raise if both, a value and a callback are set for min
    """
    with pytest.raises(ValueError) as exc_info:
        DateRange(min=date(2023, 5, 24), min_callback=_dt_callback_min)

    (err_msg,) = exc_info.value.args
    assert err_msg == "You can only specify one of min or min_callback."


def test_date_range_max_callback_and_value_set():
    """
    It should raise if both, a value and a callback are set for max
    """
    with pytest.raises(ValueError) as exc_info:
        DateRange(max=date(2023, 5, 24), max_callback=_dt_callback_max)

    (err_msg,) = exc_info.value.args
    assert err_msg == "You can only specify one of max or max_callback."
