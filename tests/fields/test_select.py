import sys
from enum import Enum
from enum import IntEnum

import pytest

from tests.common import DummyPostData
from wtforms import validators
from wtforms import widgets
from wtforms.fields import Choice
from wtforms.fields import enum_choices
from wtforms.fields import enum_coerce
from wtforms.fields import Field
from wtforms.fields import RadioField
from wtforms.fields import SelectChoice
from wtforms.fields import SelectField
from wtforms.fields import SelectMultipleField
from wtforms.form import Form

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    StrEnum = None


def make_form(name="F", **fields):
    return type(str(name), (Form,), fields)


@pytest.mark.parametrize("field_type", [SelectField, SelectMultipleField, RadioField])
@pytest.mark.parametrize("optgroup", [None, "Group"])
def test_explicit_empty_choice_labels(field_type, optgroup):
    F = make_form(
        s=field_type(
            choices=[
                SelectChoice("blank", "", optgroup=optgroup),
                SelectChoice("automatic", optgroup=optgroup),
            ]
        )
    )
    form = F(s=["blank"] if field_type is SelectMultipleField else "blank")
    options = list(form.s)
    assert options[0].label.text == ""
    assert options[1].label.text == "automatic"
    if field_type is RadioField:
        assert '<label for="s-0"></label>' in form.s()
    else:
        assert '<option selected value="blank"></option>' in form.s()
        assert '<option value="automatic">automatic</option>' in form.s()


def test_legacy_render_option_preserves_empty_label():
    labels = []

    class LegacySelect(widgets.Select):
        @classmethod
        def render_option(cls, value, label, selected, **kwargs):
            labels.append(label)
            return super().render_option(Choice(value, label, selected, kwargs))

    F = make_form(
        s=SelectField(choices=[SelectChoice("blank", "")], widget=LegacySelect())
    )
    with pytest.warns(DeprecationWarning, match="pre-3.3 signature"):
        html = F(s="blank").s()
    assert labels == [""]
    assert '<option selected value="blank"></option>' in html


def test_select_field_copies_choices():
    class F(Form):
        items = SelectField(choices=[])

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def add_choice(self, choice):
            self.items.choices.append(SelectChoice(choice, choice))

    f1 = F()
    f2 = F()

    f1.add_choice("a")
    f2.add_choice("b")

    assert f1.items.choices == [SelectChoice("a", "a")]
    assert f2.items.choices == [SelectChoice("b", "b")]
    assert f1.items.choices is not f2.items.choices


class F(Form):
    a = SelectField(
        choices=[
            SelectChoice("a", "hello"),
            SelectChoice("btest", "bye"),
        ],
        default="a",
    )
    b = SelectField(
        choices=[
            SelectChoice(1, "Item 1"),
            SelectChoice(2, "Item 2"),
        ],
        coerce=int,
        option_widget=widgets.TextInput(),
    )


def test_defaults():
    form = F()
    assert form.a.data == "a"
    assert form.b.data is None
    assert form.validate() is False
    assert form.a() == (
        '<select id="a" name="a"><option selected value="a">hello</option>'
        '<option value="btest">bye</option></select>'
    )
    assert form.b() == (
        '<select id="b" name="b"><option value="1">Item 1</option>'
        '<option value="2">Item 2</option></select>'
    )


def test_with_data():
    form = F(DummyPostData(a=["btest"]))
    assert form.a.data == "btest"
    assert form.a() == (
        '<select id="a" name="a"><option value="a">hello</option>'
        '<option selected value="btest">bye</option></select>'
    )


def test_value_coercion():
    form = F(DummyPostData(b=["2"]))
    assert form.b.data == 2
    assert form.b.validate(form)
    form = F(DummyPostData(b=["b"]))
    assert form.b.data is None
    assert not form.b.validate(form)


def test_iterable_options():
    form = F()
    first_option = list(form.a)[0]
    assert isinstance(first_option, Field)
    assert list(str(x) for x in form.a) == [
        '<option selected value="a">hello</option>',
        '<option value="btest">bye</option>',
    ]
    assert isinstance(first_option.widget, widgets.Option)
    assert isinstance(list(form.b)[0].widget, widgets.TextInput)
    assert (
        first_option(disabled=True)
        == '<option disabled selected value="a">hello</option>'
    )


def test_option_subfields_carry_parent_form():
    """Option subfields yielded by ``__iter__`` expose the enclosing form,
    matching the propagation already done for ``_meta``."""
    F = make_form(
        a=SelectField(choices=[SelectChoice("a", "Foo"), SelectChoice("b", "Bar")])
    )
    form = F()
    for opt in form.a:
        assert opt._form is form


def test_default_coerce():
    F = make_form(a=SelectField(choices=[SelectChoice("a", "Foo")]))
    form = F(DummyPostData(a=[]))
    assert not form.validate()
    assert form.a.data is None
    assert len(form.a.errors) == 1
    assert form.a.errors[0] == "Not a valid choice."


def test_validate_choices():
    F = make_form(a=SelectField(choices=[SelectChoice("a", "Foo")]))
    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.data == "b"
    assert len(form.a.errors) == 1
    assert form.a.errors[0] == "Not a valid choice."


def test_validate_choices_when_empty():
    F = make_form(a=SelectField(choices=[]))
    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.data == "b"
    assert len(form.a.errors) == 1
    assert form.a.errors[0] == "Not a valid choice."


def test_invalid_value_message():
    F = make_form(
        a=SelectField(
            choices=[SelectChoice(1, "Foo")],
            coerce=int,
            invalid_value_message="Submitted value could not be parsed.",
        )
    )
    form = F(DummyPostData(a=["x"]))
    assert not form.validate()
    assert form.a.errors == ["Submitted value could not be parsed."]


def test_invalid_choice_message():
    F = make_form(
        a=SelectField(
            choices=[SelectChoice("a", "Foo")],
            invalid_choice_message="Pick one of the available options.",
        )
    )
    form = F(DummyPostData(a=["b"]))
    assert not form.validate()
    assert form.a.errors == ["Pick one of the available options."]


def test_validate_choices_when_none():
    F = make_form(a=SelectField())
    form = F(DummyPostData(a="b"))
    with pytest.raises(TypeError, match="Choices cannot be None"):
        form.validate()


def test_dont_validate_choices():
    F = make_form(
        a=SelectField(choices=[SelectChoice("a", "Foo")], validate_choice=False)
    )
    form = F(DummyPostData(a=["b"]))
    assert form.validate()
    assert form.a.data == "b"
    assert len(form.a.errors) == 0


def test_choices_can_be_none_when_choice_validation_is_disabled():
    F = make_form(a=SelectField(validate_choice=False))
    form = F(DummyPostData(a="b"))
    assert form.validate()


def test_choice_shortcut():
    F = make_form(a=SelectField(choices=["foo", "bar"], validate_choice=False))
    form = F(a="bar")
    assert '<option value="foo">foo</option>' in form.a()


def test_choice_shortcut_post():
    F = make_form(a=SelectField(choices=["foo", "bar"]))
    form = F(DummyPostData(a=["foo"]))
    assert form.validate()
    assert form.a.data == "foo"
    assert len(form.a.errors) == 0


@pytest.mark.parametrize("choices", [[], None])
def test_empty_choice(choices):
    F = make_form(a=SelectField(choices=choices, validate_choice=False))
    form = F(a="bar")
    assert form.a() == '<select id="a" name="a"></select>'


def test_callable_choices():
    def choices():
        return ["foo", "bar"]

    F = make_form(a=SelectField(choices=choices))
    form = F(a="bar")

    assert list(str(x) for x in form.a) == [
        '<option value="foo">foo</option>',
        '<option selected value="bar">bar</option>',
    ]


def test_callable_choices_receives_form_and_field():
    """A ``(form, field)`` callable receives the bound form and field."""
    captured = []

    def choices(form, field):
        captured.append((form, field))
        return ["foo", "bar"]

    F = make_form(a=SelectField(choices=choices))
    form = F(a="bar")

    assert list(str(x) for x in form.a) == [
        '<option value="foo">foo</option>',
        '<option selected value="bar">bar</option>',
    ]
    assert captured == [(form, form.a)]


def test_requried_flag():
    F = make_form(
        c=SelectField(
            choices=[SelectChoice("a", "hello"), SelectChoice("b", "bye")],
            validators=[validators.InputRequired()],
        )
    )
    form = F(DummyPostData(c="a"))
    assert form.c() == (
        '<select id="c" name="c" required>'
        '<option selected value="a">hello</option>'
        '<option value="b">bye</option>'
        "</select>"
    )


def test_required_validator():
    F = make_form(
        c=SelectField(
            choices=[SelectChoice("a", "hello"), SelectChoice("b", "bye")],
            validators=[validators.InputRequired()],
        )
    )
    form = F(DummyPostData(c="b"))
    assert form.validate()
    assert form.c.errors == []
    form = F()
    assert form.validate() is False
    assert form.c.errors == ["This field is required."]


def test_render_kw_preserved():
    F = make_form(
        a=SelectField(choices=[("foo"), ("bar")], render_kw=dict(disabled=True))
    )
    form = F()
    assert form.a() == (
        '<select disabled id="a" name="a">'
        '<option value="foo">foo</option>'
        '<option value="bar">bar</option>'
        "</select>"
    )


def test_optgroup():
    F = make_form(a=SelectField(choices=[SelectChoice("a", "Foo", optgroup="hello")]))
    form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option selected value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        Choice("a", "Foo", selected=True, render_kw={})
    ]


def test_optgroup_shortcut():
    F = make_form(
        a=SelectField(
            choices=[
                SelectChoice("foo", optgroup="hello"),
                SelectChoice("bar", optgroup="hello"),
            ]
        )
    )
    form = F(a="bar")

    assert (
        '<optgroup label="hello">'
        '<option value="foo">foo</option>'
        '<option selected value="bar">bar</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        Choice("foo", "foo", selected=False, render_kw={}),
        Choice("bar", "bar", selected=True, render_kw={}),
    ]


def test_option_render_kw():
    F = make_form(
        a=SelectField(
            choices=[
                SelectChoice(
                    "a", "Foo", render_kw={"title": "foobar", "data-foo": "bar"}
                )
            ]
        )
    )
    form = F(a="a")

    assert (
        '<option data-foo="bar" selected title="foobar" value="a">Foo</option>'
        in form.a()
    )
    assert list(form.a.iter_choices()) == [
        Choice(
            "a",
            "Foo",
            selected=True,
            render_kw={"title": "foobar", "data-foo": "bar"},
        )
    ]


def test_optgroup_option_render_kw():
    F = make_form(
        a=SelectField(
            choices=[
                SelectChoice(
                    "a",
                    "Foo",
                    render_kw={"title": "foobar", "data-foo": "bar"},
                    optgroup="hello",
                )
            ]
        )
    )
    form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option data-foo="bar" selected title="foobar" value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        Choice(
            "a",
            "Foo",
            selected=True,
            render_kw={"title": "foobar", "data-foo": "bar"},
        )
    ]


def test_has_groups_false_without_optgroup():
    """``has_groups()`` is False when no choice carries an ``optgroup``."""
    F = make_form(
        a=SelectField(choices=[SelectChoice("a", "Foo"), SelectChoice("b", "Bar")])
    )
    assert F().a.has_groups() is False


def test_has_groups_true_with_any_optgroup():
    """``has_groups()`` is True as soon as at least one choice is grouped."""
    F = make_form(
        a=SelectField(
            choices=[
                SelectChoice("a", "Foo"),
                SelectChoice("b", "Bar", optgroup="g1"),
            ]
        )
    )
    assert F().a.has_groups() is True


def test_iter_groups_preserves_order():
    """``iter_groups()`` preserves choice order: consecutive choices sharing
    the same ``optgroup`` form one group, non-consecutive ones yield
    separate ``(optgroup, [...])`` pairs (``itertools.groupby`` semantics).
    Ungrouped choices are yielded as ``(None, [...])`` at their position."""
    F = make_form(
        a=SelectField(
            choices=[
                SelectChoice("foo", "lfoo", optgroup="g1"),
                SelectChoice("baz", "lbaz", optgroup="g2"),
                SelectChoice("abc", "labc"),
                SelectChoice("bar", "lbar", optgroup="g1"),
                SelectChoice("xyz", "lxyz"),
            ]
        )
    )
    form = F(a="foo")
    groups = list(form.a.iter_groups())

    assert groups == [
        ("g1", [Choice("foo", "lfoo", selected=True, render_kw={})]),
        ("g2", [Choice("baz", "lbaz", selected=False, render_kw={})]),
        (None, [Choice("abc", "labc", selected=False, render_kw={})]),
        ("g1", [Choice("bar", "lbar", selected=False, render_kw={})]),
        (None, [Choice("xyz", "lxyz", selected=False, render_kw={})]),
    ]


def test_iter_groups_items_unpack_as_3_2_tuples():
    """Items yielded inside each group unpack like the 3.2 4-tuple
    ``(value, label, selected, render_kw)``."""
    F = make_form(
        a=SelectField(
            choices=[SelectChoice("a", "Foo", optgroup="g")],
        )
    )
    form = F(a="a")
    for _label, items in form.a.iter_groups():
        for value, label, selected, render_kw in items:
            assert (value, label, selected, render_kw) == ("a", "Foo", True, {})


def test_dict_str_str_flat_choices():
    """``{value: label}`` is a flat shorthand for ``[SelectChoice(value, label)]``."""
    F = make_form(a=SelectField(choices={"py": "Python", "rs": "Rust"}))
    form = F(a="py")
    assert '<option selected value="py">Python</option>' in form.a()
    assert '<option value="rs">Rust</option>' in form.a()
    assert form.validate()


def test_dict_str_dict_optgroup_choices():
    """``{label: {value: label}}`` denotes optgroups."""
    F = make_form(
        a=SelectField(
            choices={
                "Compiled": {"rs": "Rust", "c": "C"},
                "Interpreted": {"py": "Python"},
            }
        )
    )
    form = F(a="rs")
    html = form.a()
    assert '<optgroup label="Compiled">' in html
    assert '<option selected value="rs">Rust</option>' in html
    assert '<optgroup label="Interpreted">' in html
    assert '<option value="py">Python</option>' in html


def test_dict_mixed_flat_and_optgroup_choices():
    """``str`` values are flat options; ``dict`` values are optgroups —
    both may appear at the top level."""
    F = make_form(
        a=SelectField(
            choices={
                "py": "Python",
                "Functional": {"hs": "Haskell", "ml": "OCaml"},
            }
        )
    )
    html = F().a()
    assert '<option value="py">Python</option>' in html
    assert '<optgroup label="Functional">' in html
    assert '<option value="hs">Haskell</option>' in html
    assert '<option value="ml">OCaml</option>' in html


def test_tuple_choices_deprecation():
    F = make_form(a=SelectField(choices=[("a", "Foo")]))
    with pytest.warns(DeprecationWarning):
        form = F(a="a")

    assert '<option selected value="a">Foo</option>' in form.a()
    assert list(form.a.iter_choices()) == [
        Choice("a", "Foo", selected=True, render_kw={})
    ]


def test_dict_choices_deprecation_with_choice_object():
    F = make_form(a=SelectField(choices={"hello": [SelectChoice("a", "Foo")]}))
    with pytest.warns(DeprecationWarning):
        form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option selected value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        Choice("a", "Foo", selected=True, render_kw={})
    ]


def test_dict_choices_deprecation_with_tuple():
    F = make_form(a=SelectField(choices={"hello": [("a", "Foo")]}))
    with pytest.warns(DeprecationWarning):
        form = F(a="a")

    assert (
        '<optgroup label="hello">'
        '<option selected value="a">Foo</option>'
        "</optgroup>" in form.a()
    )
    assert list(form.a.iter_choices()) == [
        Choice("a", "Foo", selected=True, render_kw={})
    ]


def test_self_choices_preserves_user_supplied_shape():
    """`self.choices` keeps the shape the user passed (raw tuples remain
    tuples), so subclasses doing ``for value, label in self.choices``
    per the WTForms 3.2 contract keep working."""
    F = make_form(a=SelectField(choices=[("a", "Apple"), ("b", "Banana")]))
    with pytest.warns(DeprecationWarning, match="tuples"):
        form = F()
    for value, label in form.a.choices:
        assert (value, label) in {("a", "Apple"), ("b", "Banana")}


def test_legacy_subclass_yielding_tuples_keeps_working():
    """A subclass overriding ``iter_choices`` to yield raw 4-tuples
    ``(value, label, selected, render_kw)`` per the WTForms 3.2 contract
    still renders, validates and iterates — with a ``DeprecationWarning``."""

    class LegacySelect(SelectField):
        def iter_choices(self):
            yield ("a", "Apple", self.data == "a", {})
            yield ("b", "Banana", self.data == "b", {})

    F = make_form(s=LegacySelect(choices=[SelectChoice("a"), SelectChoice("b")]))
    form = F(s="a")

    with pytest.warns(DeprecationWarning, match="raw tuples"):
        html = form.s()
    assert '<option selected value="a">Apple</option>' in html
    assert '<option value="b">Banana</option>' in html

    with pytest.warns(DeprecationWarning, match="raw tuples"):
        assert form.validate() is True

    with pytest.warns(DeprecationWarning, match="raw tuples"):
        opts = list(form.s)
    assert [(opt.checked, str(opt.label.text)) for opt in opts] == [
        (True, "Apple"),
        (False, "Banana"),
    ]


def test_legacy_subclass_yielding_3_tuples_keeps_working():
    """Pre-3.1 contract: 3-tuples ``(value, label, selected)`` also work."""

    class LegacySelect(SelectField):
        def iter_choices(self):
            yield ("a", "Apple", False)
            yield ("b", "Banana", False)

    F = make_form(s=LegacySelect(choices=[SelectChoice("a"), SelectChoice("b")]))
    form = F()
    with pytest.warns(DeprecationWarning, match="raw tuples"):
        html = form.s()
    assert '<option value="a">Apple</option>' in html


def test_iter_groups_override_yielding_tuples_keeps_working():
    """A subclass overriding ``iter_groups`` to yield raw tuples inside the
    group list still renders — with a ``DeprecationWarning``."""

    class GroupedSelect(SelectField):
        def has_groups(self):
            return True

        def iter_groups(self):
            yield "Fruits", [("a", "Apple", self.data == "a", {})]
            yield "Veggies", [("c", "Carrot", self.data == "c", {})]

    F = make_form(s=GroupedSelect(choices=[SelectChoice("a"), SelectChoice("c")]))
    form = F(s="a")
    with pytest.warns(DeprecationWarning, match="raw tuples"):
        html = form.s()
    assert '<optgroup label="Fruits">' in html
    assert '<option selected value="a">Apple</option>' in html
    assert '<optgroup label="Veggies">' in html
    assert '<option value="c">Carrot</option>' in html


class _Plain(Enum):
    RED = 1
    GREEN = 2


class _Pretty(Enum):
    RED = 1
    GREEN = 2

    def __str__(self):
        return self.name.title()


class _Level(IntEnum):
    LOW = 1
    HIGH = 2


class _Provider(Enum):
    GITHUB = "github"
    GITLAB = "gitlab"


def test_enum_choices_default_value():
    """By default the HTML value is ``member.value``."""
    assert enum_choices(_Provider) == [
        SelectChoice(value="github", label="GITHUB"),
        SelectChoice(value="gitlab", label="GITLAB"),
    ]


def test_enum_choices_by_name():
    """``by="name"`` puts ``member.name`` on the wire."""
    assert enum_choices(_Plain, by="name") == [
        SelectChoice(value="RED", label="RED"),
        SelectChoice(value="GREEN", label="GREEN"),
    ]


def test_enum_choices_dunder_str_label():
    """An Enum overriding ``__str__`` uses ``str(member)`` as label."""
    assert enum_choices(_Pretty) == [
        SelectChoice(value=1, label="Red"),
        SelectChoice(value=2, label="Green"),
    ]


@pytest.mark.skipif(sys.version_info < (3, 11), reason="StrEnum requires 3.11+")
def test_enum_choices_strenum():
    """StrEnum uses ``str(member)`` (the value) for both value and label."""

    class _Status(StrEnum):
        ACTIVE = "active"
        INACTIVE = "inactive"

    assert enum_choices(_Status) == [
        SelectChoice(value="active", label="active"),
        SelectChoice(value="inactive", label="inactive"),
    ]


def test_enum_choices_intenum_label():
    """IntEnum has no ``__str__`` injected; label falls back to ``member.name``."""
    assert enum_choices(_Level) == [
        SelectChoice(value=1, label="LOW"),
        SelectChoice(value=2, label="HIGH"),
    ]


def test_enum_choices_custom_label():
    """A ``label=`` callable overrides the default."""
    assert enum_choices(_Provider, label=lambda m: m.name.title()) == [
        SelectChoice(value="github", label="Github"),
        SelectChoice(value="gitlab", label="Gitlab"),
    ]


def test_enum_choices_invalid_by():
    """An unknown ``by`` is rejected."""
    with pytest.raises(ValueError):
        enum_choices(_Provider, by="bogus")


def test_enum_coerce_value_round_trip():
    """The default ``enum_coerce`` round-trips ``member.value``."""
    F = make_form(
        a=SelectField(
            choices=enum_choices(_Provider),
            coerce=enum_coerce(_Provider),
        )
    )
    form = F(DummyPostData(a=["github"]))
    assert form.a.data is _Provider.GITHUB
    assert form.validate()


def test_enum_coerce_intenum_value_round_trip():
    """``enum_coerce`` resolves through ``str(value)``, so IntEnum round-trips."""
    F = make_form(
        a=SelectField(
            choices=enum_choices(_Level),
            coerce=enum_coerce(_Level),
        )
    )
    form = F(DummyPostData(a=["1"]))
    assert form.a.data is _Level.LOW
    assert form.validate()


def test_enum_coerce_by_name_round_trip():
    """``by="name"`` round-trips ``member.name``."""
    F = make_form(
        a=SelectField(
            choices=enum_choices(_Plain, by="name"),
            coerce=enum_coerce(_Plain, by="name"),
        )
    )
    form = F(DummyPostData(a=["RED"]))
    assert form.a.data is _Plain.RED
    assert form.validate()


def test_enum_coerce_accepts_member():
    """``enum_coerce`` accepts an already-coerced member without re-lookup."""
    F = make_form(
        a=SelectField(
            choices=enum_choices(_Provider),
            coerce=enum_coerce(_Provider),
        )
    )
    form = F(a=_Provider.GITLAB)
    assert form.a.data is _Provider.GITLAB


def test_enum_coerce_invalid():
    """An unknown submitted value fails validation cleanly (KeyError → ValueError)."""
    F = make_form(
        a=SelectField(
            choices=enum_choices(_Provider),
            coerce=enum_coerce(_Provider),
        )
    )
    form = F(DummyPostData(a=["nope"]))
    assert not form.validate()
    assert form.a.data is None
    assert "Invalid Choice: could not coerce." in form.a.errors


def test_enum_coerce_invalid_by():
    """An unknown ``by`` is rejected."""
    with pytest.raises(ValueError):
        enum_coerce(_Provider, by="bogus")


def test_select_field_enum_class_as_coerce():
    """A string-valued Enum works as ``coerce`` directly (standard lookup)."""
    F = make_form(
        a=SelectField(
            choices=enum_choices(_Provider),
            coerce=_Provider,
        )
    )
    form = F(DummyPostData(a=["github"]))
    assert form.a.data is _Provider.GITHUB
    assert form.validate()


def test_select_field_coerce_passed_through():
    """``coerce`` is stored as provided — no implicit wrapping."""
    F = make_form(a=SelectField(choices=[SelectChoice("x", "X")], coerce=_Plain))
    assert F().a.coerce is _Plain


def test_iter_choices_tuple_unpacking():
    """``iter_choices()`` yields ``Choice`` 4-tuples — unpacking matches the
    3.2 yield shape ``(value, label, selected, render_kw)``."""
    F = make_form(
        a=SelectField(choices=[SelectChoice("a", "Foo"), SelectChoice("b", "Bar")])
    )
    form = F(a="a")
    unpacked = [(v, lab, sel, rk) for v, lab, sel, rk in form.a.iter_choices()]
    assert unpacked == [("a", "Foo", True, {}), ("b", "Bar", False, {})]


def test_select_field_enum_renders_selected():
    """Pre-selecting a member highlights the right option."""
    F = make_form(
        a=SelectField(
            choices=enum_choices(_Provider),
            coerce=enum_coerce(_Provider),
        )
    )
    form = F(a=_Provider.GITLAB)
    assert '<option selected value="gitlab">GITLAB</option>' in form.a()
