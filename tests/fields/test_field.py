import pytest
from markupsafe import Markup

from tests.common import DummyPostData
from wtforms import meta
from wtforms import validators
from wtforms.fields import Field
from wtforms.fields import StringField
from wtforms.form import Form


class F(Form):
    a = StringField(default="hello", render_kw={"readonly": True, "foo": "bar"})
    b = StringField(validators=[validators.InputRequired()])


def test_unbound_field():
    unbound = F.a
    assert unbound.creation_counter != 0
    assert unbound.field_class is StringField
    assert unbound.args == ()
    assert unbound.kwargs == {
        "default": "hello",
        "render_kw": {"readonly": True, "foo": "bar"},
    }
    assert repr(unbound).startswith("<UnboundField(StringField")


def test_htmlstring():
    assert isinstance(F().a.__html__(), Markup)


def test_str_coerce():
    field = F().a
    assert isinstance(str(field), str)
    assert str(field) == str(field)


def test_unicode_coerce():
    field = F().a
    assert str(field) == field()


def test_process_formdata():
    field = F().a
    Field.process_formdata(field, [42])
    assert field.data == 42


def test_errors_are_a_list_before_validation():
    field = F().a
    assert field.errors == []
    assert field.process_errors == []
    field.errors.append("some error")
    assert field.errors == ["some error"]


def test_meta_attribute():
    # Can we pass in meta via _form?
    form = F()
    assert form.a.meta is form.meta

    # Can we pass in meta via _meta?
    form_meta = meta.DefaultMeta()
    field = StringField(name="Foo", _form=None, _meta=form_meta)
    assert field.meta is form_meta

    # Do we fail if both _meta and _form are None?
    with pytest.raises(TypeError):
        StringField(name="foo", _form=None)


def test_render_kw():
    form = F()
    assert (
        form.a()
        == '<input foo="bar" id="a" name="a" readonly type="text" value="hello">'
    )
    assert (
        form.a(foo="baz")
        == '<input foo="baz" id="a" name="a" readonly type="text" value="hello">'
    )
    assert form.a(foo="baz", readonly=False, other="hello") == (
        '<input foo="baz" id="a" name="a" other="hello" type="text" value="hello">'
    )


def test_render_special():
    class F(Form):
        s = StringField(render_kw={"class_": "foo"})

    assert F().s() == '<input class="foo" id="s" name="s" type="text" value="">'
    assert (
        F().s(**{"class": "bar"})
        == '<input class="bar" id="s" name="s" type="text" value="">'
    )
    assert (
        F().s(**{"class_": "bar"})
        == '<input class="bar" id="s" name="s" type="text" value="">'
    )

    class G(Form):
        s = StringField(render_kw={"class__": "foo"})

    assert G().s() == '<input class="foo" id="s" name="s" type="text" value="">'
    assert (
        G().s(**{"class__": "bar"})
        == '<input class="bar" id="s" name="s" type="text" value="">'
    )

    class H(Form):
        s = StringField(render_kw={"for_": "foo"})

    assert H().s() == '<input for="foo" id="s" name="s" type="text" value="">'
    assert (
        H().s(**{"for": "bar"})
        == '<input for="bar" id="s" name="s" type="text" value="">'
    )
    assert (
        H().s(**{"for_": "bar"})
        == '<input for="bar" id="s" name="s" type="text" value="">'
    )


def test_required_flag():
    form = F()
    assert form.b() == '<input id="b" name="b" required type="text" value="">'


def test_check_validators():
    v1 = "Not callable"
    v2 = validators.DataRequired

    with pytest.raises(
        TypeError,
        match=rf"{v1} is not a valid validator because it is not callable",
    ):
        Field(validators=[v1])

    with pytest.raises(
        TypeError,
        match=rf"{v2} is not a valid validator because "
        "it is a class, it should be an "
        "instance",
    ):
        Field(validators=[v2])


def test_custom_name():
    class F(Form):
        foo = StringField(name="bar", default="default")
        x = StringField()

    class ObjFoo:
        foo = "obj"

    class ObjBar:
        bar = "obj"

    f = F(DummyPostData(foo="data"))
    assert f.foo.data == "default"
    assert 'value="default"' in f.foo()

    f = F(DummyPostData(bar="data"))
    assert f.foo.data == "data"
    assert 'value="data"' in f.foo()

    f = F(foo="kwarg")
    assert f.foo.data == "kwarg"
    assert 'value="kwarg"' in f.foo()

    f = F(bar="kwarg")
    assert f.foo.data == "default"
    assert 'value="default"' in f.foo()

    f = F(obj=ObjFoo())
    assert f.foo.data == "obj"
    assert 'value="obj"' in f.foo()

    f = F(obj=ObjBar())
    assert f.foo.data == "default"
    assert 'value="default"' in f.foo()


class PrePostTestField(StringField):
    def pre_validate(self, form):
        if self.data == "stoponly":
            raise validators.StopValidation()
        elif self.data.startswith("stop"):
            raise validators.StopValidation("stop with message")

    def post_validate(self, form, stopped):
        if self.data == "p":
            raise validators.ValidationError("Post")
        elif stopped and self.data == "stop-post":
            raise validators.ValidationError("Post-stopped")


def _init_field(value):
    class F(Form):
        a = PrePostTestField(validators=[validators.Length(max=1, message="too long")])

    form = F(a=value)
    form.validate()
    return form.a


def test_pre_stop():
    a = _init_field("long")
    assert a.errors == ["too long"]

    stoponly = _init_field("stoponly")
    assert stoponly.errors == []

    stopmessage = _init_field("stopmessage")
    assert stopmessage.errors == ["stop with message"]


def test_post():
    a = _init_field("p")
    assert a.errors == ["Post"]
    stopped = _init_field("stop-post")
    assert stopped.errors == ["stop with message", "Post-stopped"]
