from decimal import Decimal
from decimal import ROUND_DOWN
from decimal import ROUND_UP

from tests.common import DummyPostData
from wtforms.fields import DecimalField
from wtforms.form import Form


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


def test_decimal_field():
    F = make_form(a=DecimalField())
    form = F(DummyPostData(a="2.1"))
    assert form.a.data == Decimal("2.1")
    assert form.a._value() == "2.1"
    form.a.raw_data = None
    assert form.a._value() == "2.10"
    assert form.validate()
    form = F(DummyPostData(a="2,1"), a=Decimal(5))
    assert form.a.data is None
    assert form.a.raw_data == ["2,1"]
    assert not form.validate()
    form = F(DummyPostData(a="asdf"), a=Decimal(".21"))
    assert form.a._value() == "asdf"
    assert not form.validate()


def test_quantize():
    F = make_form(
        a=DecimalField(places=3, rounding=ROUND_UP), b=DecimalField(places=None)
    )
    form = F(a=Decimal("3.1415926535"))
    assert form.a._value() == "3.142"
    form.a.rounding = ROUND_DOWN
    assert form.a._value() == "3.141"
    assert form.b._value() == ""
    form = F(a=3.14159265, b=72)
    assert form.a._value() == "3.142"
    assert isinstance(form.a.data, float)
    assert form.b._value() == "72"


def test_invalid_value_message():
    F = make_form(a=DecimalField(invalid_value_message="Enter a decimal number."))
    form = F(DummyPostData(a=["x"]))
    assert not form.validate()
    assert form.a.errors == ["Enter a decimal number."]


def test_invalid_value_type():
    F = make_form(a=DecimalField())
    form = F(DummyPostData(a={"not a": "decimal"}))

    assert form.a.data is None
    assert not form.validate()
    assert form.a.errors == ["Not a valid decimal value."]
