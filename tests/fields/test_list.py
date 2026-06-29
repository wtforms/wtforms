from collections import namedtuple

import pytest

from tests.common import DummyPostData
from wtforms import validators
from wtforms.fields import FieldList
from wtforms.fields import FormField
from wtforms.fields import SelectField
from wtforms.fields import StringField
from wtforms.form import Form
from wtforms.meta import DefaultMeta


class AttrDict:
    def __init__(self, *args, **kw):
        self.__dict__.update(*args, **kw)


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


t = StringField(validators=[validators.DataRequired()])


def test_form():
    F = make_form(a=FieldList(t))
    data = ["foo", "hi", "rawr"]
    a = F(a=data).a
    assert a.entries[1].data == "hi"
    assert a.entries[1].name == "a-1"
    assert a.data == data
    assert len(a.entries) == 3

    pdata = DummyPostData(
        {"a-0": ["bleh"], "a-3": ["yarg"], "a-4": [""], "a-7": ["mmm"]}
    )
    form = F(pdata)
    assert len(form.a.entries) == 4
    assert form.a.data == ["bleh", "yarg", "", "mmm"]
    assert not form.validate()

    form = F(pdata, a=data)
    assert form.a.data == ["bleh", "yarg", "", "mmm"]
    assert not form.validate()

    # Test for formdata precedence
    pdata = DummyPostData({"a-0": ["a"], "a-1": ["b"]})
    form = F(pdata, a=data)
    assert len(form.a.entries) == 2
    assert form.a.data == ["a", "b"]
    assert list(iter(form.a)) == list(form.a.entries)


def test_enclosed_subform():
    def make_inner():
        return AttrDict(a=None)

    F = make_form(a=FieldList(FormField(make_form("FChild", a=t), default=make_inner)))
    data = [{"a": "hello"}]
    form = F(a=data)
    assert form.a.data == data
    assert form.validate()
    form.a.append_entry()
    assert form.a.data == data + [{"a": None}]
    assert not form.validate()

    pdata = DummyPostData({"a-0": ["fake"], "a-0-a": ["foo"], "a-1-a": ["bar"]})
    form = F(pdata, a=data)
    assert form.a.data == [{"a": "foo"}, {"a": "bar"}]

    inner_obj = make_inner()
    inner_list = [inner_obj]
    obj = AttrDict(a=inner_list)
    form.populate_obj(obj)
    assert obj.a is not inner_list
    assert len(obj.a) == 2
    assert obj.a[0] is inner_obj
    assert obj.a[0].a == "foo"
    assert obj.a[1].a == "bar"

    # Test failure on populate
    obj2 = AttrDict(a=42)
    with pytest.raises(TypeError):
        form.populate_obj(obj2)


def test_enclosed_subform_custom_name():
    class Inside(Form):
        foo = StringField(name="bar", default="default")

    class Outside(Form):
        subforms = FieldList(FormField(Inside), min_entries=1)

    o = Outside()
    assert o.subforms[0].foo.data == "default"

    pdata = DummyPostData({"subforms-0-bar": "form"})
    o = Outside(pdata)
    assert o.subforms[0].foo.data == "form"

    pdata = DummyPostData({"subforms-0-foo": "form"})
    o = Outside(pdata)
    assert o.subforms[0].foo.data == "default"


def test_custom_separator():
    F = make_form(a=FieldList(t, separator="_"))

    pdata = DummyPostData({"a_0": "0_a", "a_1": "1_a"})
    f = F(pdata)
    assert f.a[0].data == "0_a"
    assert f.a[1].data == "1_a"


def test_enclosed_subform_list_separator():
    class Inside(Form):
        foo = StringField(default="default")

    class Outside(Form):
        subforms = FieldList(FormField(Inside), min_entries=1, separator="_")

    o = Outside()
    assert o.subforms[0].foo.data == "default"
    assert o.subforms[0].foo.name == "subforms_0-foo"

    pdata = DummyPostData({"subforms_0-foo": "0-foo", "subforms_1-foo": "1-foo"})
    o = Outside(pdata)
    assert o.subforms[0].foo.data == "0-foo"
    assert o.subforms[1].foo.data == "1-foo"


def test_enclosed_subform_uniform_separators():
    class Inside(Form):
        foo = StringField(default="default")

    class Outside(Form):
        subforms = FieldList(
            FormField(Inside, separator="_"), min_entries=1, separator="_"
        )

    o = Outside()
    assert o.subforms[0].foo.data == "default"
    assert o.subforms[0].foo.name == "subforms_0_foo"

    pdata = DummyPostData({"subforms_0_foo": "0_foo", "subforms_1_foo": "1_foo"})
    o = Outside(pdata)
    assert o.subforms[0].foo.data == "0_foo"
    assert o.subforms[1].foo.data == "1_foo"


def test_enclosed_subform_mixed_separators():
    class Inside(Form):
        foo = StringField(default="default")

    class Outside(Form):
        subforms = FieldList(FormField(Inside, separator="_"), min_entries=1)

    o = Outside()
    assert o.subforms[0].foo.data == "default"
    assert o.subforms[0].foo.name == "subforms-0_foo"

    pdata = DummyPostData({"subforms-0_foo": "0_foo", "subforms-1_foo": "1_foo"})
    o = Outside(pdata)
    assert o.subforms[0].foo.data == "0_foo"
    assert o.subforms[1].foo.data == "1_foo"


def test_entry_management():
    F = make_form(a=FieldList(t))
    a = F(a=["hello", "bye"]).a
    assert a.pop_entry().name == "a-1"
    assert a.data == ["hello"]
    a.append_entry("orange")
    assert a.data == ["hello", "orange"]
    assert a[-1].name == "a-1"
    assert a.pop_entry().data == "orange"
    assert a.pop_entry().name == "a-0"
    with pytest.raises(IndexError):
        a.pop_entry()


def test_entry_management_by_index():
    F = make_form(a=FieldList(t))
    a = F(a=["hello", "bye", "later"]).a

    assert a.pop_entry(1).data == "bye"
    assert a.data == ["hello", "later"]
    assert [entry.name for entry in a.entries] == ["a-0", "a-1"]

    inserted = a.insert_entry(1, "orange")
    assert inserted.name == "a-1"
    assert a.data == ["hello", "orange", "later"]
    assert [entry.name for entry in a.entries] == ["a-0", "a-1", "a-2"]

    assert a.pop_entry(1).data == "orange"
    assert a.data == ["hello", "later"]

    appended = a.append_entry("grape")
    assert appended.name == "a-2"
    assert a.data == ["hello", "later", "grape"]


def test_entry_management_by_index_with_subforms():
    class Inside(Form):
        foo = StringField()

    F = make_form(a=FieldList(FormField(Inside)))
    a = F(a=[{"foo": "hello"}, {"foo": "bye"}]).a

    inserted = a.insert_entry(1, {"foo": "orange"})
    assert a.data == [{"foo": "hello"}, {"foo": "orange"}, {"foo": "bye"}]
    assert inserted.foo.name == "a-1-foo"
    assert [entry.foo.name for entry in a.entries] == ["a-0-foo", "a-1-foo", "a-2-foo"]

    assert a.pop_entry(1).foo.data == "orange"
    assert a.data == [{"foo": "hello"}, {"foo": "bye"}]
    assert [entry.foo.name for entry in a.entries] == ["a-0-foo", "a-1-foo"]


def test_gap_compacted_through_formdata_round_trip():
    """A formdata with gaps in indices is compacted on read: entries are
    rebuilt with consecutive indices, preserving formdata key order."""
    F = make_form(a=FieldList(t))
    pdata = DummyPostData([("a-0", "hello"), ("a-2", "later")])
    a = F(pdata).a
    assert [entry.name for entry in a.entries] == ["a-0", "a-1"]
    assert a.data == ["hello", "later"]
    appended = a.append_entry("grape")
    assert appended.name == "a-2"


def test_entry_index_attribute_reflects_position():
    """``field.index`` always reflects the entry's current position; mutations
    via :meth:`insert_entry` or :meth:`pop_entry` renumber entries to
    consecutive ``[0..N-1]``."""
    F = make_form(a=FieldList(t))
    a = F(a=["A", "B", "C"]).a
    assert [e.index for e in a.entries] == [0, 1, 2]

    a.pop_entry(0)
    assert [e.index for e in a.entries] == [0, 1]

    inserted = a.insert_entry(0, "X")
    assert inserted.index == 0
    assert [e.index for e in a.entries] == [0, 1, 2]


def test_formdata_index_drives_entry_order():
    """The numeric index encoded in ``name="a-N"`` drives the entry position,
    regardless of formdata key order. HTTP clients are free to serialize
    keys in any order — only the ``N`` in the name carries the position."""
    F = make_form(a=FieldList(t))
    pdata = DummyPostData([("a-2", "second"), ("a-0", "first"), ("a-1", "middle")])
    a = F(pdata).a
    assert [(e.name, e.data) for e in a.entries] == [
        ("a-0", "first"),
        ("a-1", "middle"),
        ("a-2", "second"),
    ]


def test_min_max_entries():
    F = make_form(a=FieldList(t, min_entries=1, max_entries=3))
    a = F().a
    assert len(a) == 1
    assert a[0].data is None
    big_input = ["foo", "flaf", "bar", "baz"]
    with pytest.raises(AssertionError):
        F(a=big_input)
    pdata = DummyPostData((f"a-{i}", v) for i, v in enumerate(big_input))
    a = F(pdata).a
    assert a.data == ["foo", "flaf", "bar"]
    with pytest.raises(AssertionError):
        a.append_entry()


def test_validators():
    def validator(form, field):
        if field.data and field.data[0] == "fail":
            raise validators.ValidationError("fail")
        elif len(field.data) > 2:
            raise validators.ValidationError("too many")

    F = make_form(a=FieldList(t, validators=[validator]))

    # Case 1: length checking validators work as expected.
    fdata = DummyPostData({"a-0": ["hello"], "a-1": ["bye"], "a-2": ["test3"]})
    form = F(fdata)
    assert not form.validate()
    assert form.a.errors == ["too many"]

    # Case 2: checking a value within.
    fdata["a-0"] = ["fail"]
    form = F(fdata)
    assert not form.validate()
    assert form.a.errors == ["fail"]

    # Case 3: normal field validator still works
    form = F(DummyPostData({"a-0": [""]}))
    assert not form.validate()
    assert form.a.errors == [["This field is required."]]


def test_no_filters():
    with pytest.raises(TypeError):
        FieldList(t, filters=[str], _form=Form(), name="foo")


def test_process_prefilled():
    data = ["foo", "hi", "rawr"]
    Obj = namedtuple("Obj", "a")
    obj = Obj(data)
    F = make_form(a=FieldList(t))
    # fill form
    form = F(obj=obj)
    assert len(form.a.entries) == 3
    # pretend to submit form unchanged
    pdata = DummyPostData({"a-0": ["foo"], "a-1": ["hi"], "a-2": ["rawr"]})
    form.process(formdata=pdata)
    # check if data still the same
    assert len(form.a.entries) == 3
    assert form.a.data == data


def test_process_resets_last_index():
    F = make_form(a=FieldList(t, min_entries=1))
    form = F()

    assert form.a.last_index == 0
    assert [entry.name for entry in form.a.entries] == ["a-0"]

    form.a.process(None, ["foo", "bar"])
    assert form.a.last_index == 1
    assert [entry.name for entry in form.a.entries] == ["a-0", "a-1"]
    assert form.a.data == ["foo", "bar"]

    form.a.process(None, ["baz"])
    assert form.a.last_index == 0
    assert [entry.name for entry in form.a.entries] == ["a-0"]
    assert form.a.data == ["baz"]


def test_errors():
    F = make_form(a=FieldList(t))
    form = F(DummyPostData({"a-0": ["a"], "a-1": ""}))
    assert not form.validate()
    assert form.a.errors == [[], ["This field is required."]]


def test_add_entry_routes_through_meta_bind_field():
    """_add_entry must call meta.bind_field, just as the form constructor does.

    Without this, a custom Meta.bind_field override is silently bypassed for
    all FieldList entries — whether created at construction time (via process)
    or later via append_entry.
    """

    class TrackingMeta(DefaultMeta):
        def bind_field(self, form, unbound_field, options):
            field = super().bind_field(form, unbound_field, options)
            field._bound_via_meta = True
            return field

    class F(Form):
        class Meta(TrackingMeta):
            pass

        items = FieldList(StringField())

    pdata = DummyPostData({"items-0": "a", "items-1": "b"})
    form = F(pdata)
    for entry in form.items.entries:
        assert getattr(entry, "_bound_via_meta", False)

    form.items.append_entry("c")
    assert getattr(form.items[-1], "_bound_via_meta", False)


def test_formdata_with_sparse_indices_keeps_entry_obj_alignment():
    """Non-consecutive indices in formdata still align each entry with the obj
    at the same index, and ``populate_obj`` produces the collection without the
    missing slot."""

    class Inside(Form):
        street = StringField()

    class Outside(Form):
        addresses = FieldList(FormField(Inside))

    a0 = AttrDict(street="A street")
    a1 = AttrDict(street="B street")
    a2 = AttrDict(street="C street")
    user = AttrDict(addresses=[a0, a1, a2])

    pdata = DummyPostData(
        {
            "addresses-0-street": "A street updated",
            "addresses-2-street": "C street updated",
        }
    )
    form = Outside(pdata, obj=user)

    form.populate_obj(user)

    assert user.addresses[0] is a0
    assert user.addresses[0].street == "A street updated"
    assert user.addresses[1] is a2
    assert user.addresses[1].street == "C street updated"
    assert a1 not in user.addresses
    assert a1.street == "B street"


def test_append_entry_runs_choices_callback():
    """A SelectField choices callable nested in a FormField entry must be
    evaluated when the entry is added via append_entry, just as it would be
    during the form's normal processing cycle. The callable is invoked in
    SelectField.post_process, so append_entry must trigger it."""

    def get_choices(form, field):
        return [("a", "A"), ("b", "B")]

    class Inner(Form):
        sel = SelectField(choices=get_choices)

    F = make_form(items=FieldList(FormField(Inner)))
    html = F().items.append_entry().sel()

    assert '<option value="a">A</option>' in html
    assert '<option value="b">B</option>' in html


def test_insert_entry_runs_choices_callback():
    """Same as append_entry, but the entry is created via insert_entry. The
    callable is invoked after the renumbering, so the rendered field carries
    the compacted name."""

    def get_choices(form, field):
        return [("a", "A"), ("b", "B")]

    class Inner(Form):
        sel = SelectField(choices=get_choices)

    F = make_form(items=FieldList(FormField(Inner)))
    html = F().items.insert_entry(0).sel()

    assert 'name="items-0-sel"' in html
    assert '<option value="a">A</option>' in html
    assert '<option value="b">B</option>' in html
