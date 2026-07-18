from datetime import date

from tests.common import DummyPostData
from wtforms.fields import DateField
from wtforms.form import Form


class F(Form):
    a = DateField()
    b = DateField(format="%m/%d %Y")
    c = DateField(format="%-m/%-d %Y")


def test_basic():
    d = date(2008, 5, 7)
    form = F(DummyPostData(a=["2008-05-07"], b=["05/07", "2008"], c=["5/7 2008"]))
    assert form.a.data == d
    assert form.a._value() == "2008-05-07"
    assert form.b.data == d
    assert form.b._value() == "05/07 2008"
    assert form.c.data == d
    assert form.c._value() == "5/7 2008"


def test_failure():
    form = F(DummyPostData(a=["2008-bb-cc"], b=["hi"]))
    assert not form.validate()
    assert len(form.a.process_errors) == 1
    assert len(form.a.errors) == 1
    assert len(form.b.errors) == 1
    assert form.a.process_errors[0] == "Not a valid date value."


def test_invalid_value_message():
    class G(Form):
        a = DateField(invalid_value_message="Enter a date as YYYY-MM-DD.")

    form = G(DummyPostData(a=["bogus"]))
    assert not form.validate()
    assert form.a.errors == ["Enter a date as YYYY-MM-DD."]


def test_initial_string_data_renders():
    form = F(data={"a": "2020-01-02"})
    assert form.a.data == "2020-01-02"
    assert form.a._value() == "2020-01-02"


def test_initial_non_date_obj_attribute_renders():
    form = F(obj=type("O", (), {"a": "not-a-date"})())
    assert form.a._value() == "not-a-date"
