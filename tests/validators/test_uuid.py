import uuid

import pytest

from wtforms.validators import UUID
from wtforms.validators import ValidationError


@pytest.mark.parametrize(
    "uuid_val",
    [
        "2bc1c94f-0deb-43e9-92a1-4775189ec9f8",
        "2bc1c94f0deb43e992a14775189ec9f8",
        uuid.UUID("2bc1c94f-0deb-43e9-92a1-4775189ec9f8"),
    ],
)
def test_valid_uuid_passes(uuid_val, dummy_form, dummy_field):
    """
    Valid UUID should pass without raising
    """
    validator = UUID()
    dummy_field.data = uuid_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "uuid_val",
    [
        "2bc1c94f-deb-43e9-92a1-4775189ec9f8",
        "2bc1c94f-0deb-43e9-92a1-4775189ec9f",
        "gbc1c94f-0deb-43e9-92a1-4775189ec9f8",
        "2bc1c94f 0deb-43e9-92a1-4775189ec9f8",
    ],
)
def test_bad_uuid_raises(uuid_val, dummy_form, dummy_field):
    """
    Bad UUID should raise ValueError
    """
    validator = UUID()
    dummy_field.data = uuid_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)
