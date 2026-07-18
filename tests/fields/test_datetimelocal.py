import os
from datetime import datetime
from datetime import timezone
from zoneinfo import ZoneInfo

from tests.common import DummyPostData
from wtforms.fields import DateTimeLocalField
from wtforms.form import Form


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


class F(Form):
    a = DateTimeLocalField()
    b = DateTimeLocalField(format="%Y-%m-%d %H:%M")
    c = DateTimeLocalField(
        format="%#m/%#d/%Y %#I:%M" if os.name == "nt" else "%-m/%-d/%Y %-I:%M"
    )


def test_basic():
    d = datetime(2008, 5, 5, 4, 30, 0, 0)
    # Basic test with both inputs
    form = F(
        DummyPostData(
            a=["2008-05-05", "04:30:00"], b=["2008-05-05 04:30"], c=["5/5/2008 4:30"]
        )
    )
    assert form.a.data == d
    assert (
        form.a()
        == '<input id="a" name="a" type="datetime-local" value="2008-05-05 04:30:00">'
    )
    assert form.b.data == d
    assert (
        form.b()
        == '<input id="b" name="b" type="datetime-local" value="2008-05-05 04:30">'
    )
    assert form.c.data == d
    assert (
        form.c()
        == '<input id="c" name="c" type="datetime-local" value="5/5/2008 4:30">'
    )
    assert form.validate()

    # Test with a missing input
    form = F(DummyPostData(a=["2008-05-05"]))
    assert not form.validate()
    assert form.a.errors[0] == "Not a valid datetime value."

    form = F(a=d, b=d, c=d)
    assert form.validate()
    assert form.a._value() == "2008-05-05 04:30:00"
    assert form.b._value() == "2008-05-05 04:30"
    assert form.c._value() == "5/5/2008 4:30"


def test_microseconds():
    d = datetime(2011, 5, 7, 3, 23, 14, 424200)
    F = make_form(a=DateTimeLocalField(format="%Y-%m-%d %H:%M:%S.%f"))
    form = F(DummyPostData(a=["2011-05-07 03:23:14.4242"]))
    assert d == form.a.data


def test_separators():
    dt = datetime(2008, 5, 5, 4, 30, 0, 0)

    form = F(DummyPostData(a=["2008-05-05 04:30:00"]))
    assert form.a.data == dt
    assert form.validate()

    form = F(DummyPostData(a=["2008-05-05T04:30:00"]))
    assert form.a.data == dt
    assert form.validate()


def test_tz_attaches_tzinfo_on_submit():
    """Submitted naive value gets the field's ``tz`` attached."""
    paris = ZoneInfo("Europe/Paris")
    F = make_form(a=DateTimeLocalField(tz=paris))
    form = F(DummyPostData(a=["2026-05-06T16:00:00"]))
    assert form.a.data == datetime(2026, 5, 6, 16, 0, tzinfo=paris)


def test_tz_converts_aware_data_at_render():
    """Aware ``data`` is converted to ``tz`` and stripped before rendering."""
    paris = ZoneInfo("Europe/Paris")
    F = make_form(a=DateTimeLocalField(tz=paris))
    form = F(a=datetime(2026, 5, 6, 14, 0, tzinfo=timezone.utc))
    # 14:00 UTC == 16:00 Europe/Paris on 2026-05-06 (CEST, UTC+2)
    assert form.a._value() == "2026-05-06 16:00:00"


def test_tz_round_trip_through_utc():
    """Submitted local time round-trips correctly when reconverted to UTC."""
    paris = ZoneInfo("Europe/Paris")
    F = make_form(a=DateTimeLocalField(tz=paris))
    form = F(DummyPostData(a=["2026-05-06T16:00:00"]))
    assert form.a.data is not None
    stored = form.a.data.astimezone(timezone.utc)
    assert stored == datetime(2026, 5, 6, 14, 0, tzinfo=timezone.utc)


def test_tz_callable_resolved_lazily():
    """A callable ``tz`` is resolved at each access, not at construction."""
    paris = ZoneInfo("Europe/Paris")
    holder = {"tz": paris}
    F = make_form(a=DateTimeLocalField(tz=lambda: holder["tz"]))
    form = F(DummyPostData(a=["2026-05-06T16:00:00"]))
    assert form.a.data == datetime(2026, 5, 6, 16, 0, tzinfo=paris)

    new_york = ZoneInfo("America/New_York")
    holder["tz"] = new_york
    form = F(DummyPostData(a=["2026-05-06T10:00:00"]))
    assert form.a.data == datetime(2026, 5, 6, 10, 0, tzinfo=new_york)


def test_tz_callable_returning_none_falls_back_to_naive():
    """A callable returning ``None`` is treated as no timezone configured."""
    F = make_form(a=DateTimeLocalField(tz=lambda: None))
    form = F(DummyPostData(a=["2026-05-06T16:00:00"]))
    assert form.a.data == datetime(2026, 5, 6, 16, 0)
    assert form.a.data.tzinfo is None


def test_tz_none_keeps_legacy_naive_behavior():
    """Without ``tz``, the field preserves the pre-3.3 naive behavior."""
    F = make_form(a=DateTimeLocalField())
    form = F(DummyPostData(a=["2026-05-06T16:00:00"]))
    assert form.a.data == datetime(2026, 5, 6, 16, 0)
    assert form.a.data.tzinfo is None


def test_tz_naive_data_rendered_unchanged():
    """Naive ``data`` is rendered as-is even when ``tz`` is set."""
    paris = ZoneInfo("Europe/Paris")
    F = make_form(a=DateTimeLocalField(tz=paris))
    form = F(a=datetime(2026, 5, 6, 16, 0))
    assert form.a._value() == "2026-05-06 16:00:00"


def test_initial_string_data_renders():
    class G(Form):
        a = DateTimeLocalField()

    form = G(data={"a": "2020-01-02T03:04"})
    assert form.a._value() == "2020-01-02T03:04"
