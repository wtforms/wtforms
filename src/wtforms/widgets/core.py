import warnings

from markupsafe import escape
from markupsafe import Markup

from wtforms._compat import get_signature

__all__ = (
    "Button",
    "CheckboxInput",
    "ColorInput",
    "DataListWidget",
    "DateInput",
    "DateTimeInput",
    "DateTimeLocalInput",
    "EmailInput",
    "FileInput",
    "HiddenInput",
    "ListWidget",
    "MonthInput",
    "NumberInput",
    "Option",
    "PasswordInput",
    "RadioInput",
    "RangeInput",
    "SearchInput",
    "Select",
    "SubmitInput",
    "TableWidget",
    "TextArea",
    "TextInput",
    "TelInput",
    "TimeInput",
    "URLInput",
    "WeekInput",
)


def clean_key(key):
    key = key.rstrip("_")
    if key.startswith("data_") or key.startswith("aria_"):
        key = key.replace("_", "-")
    return key


def html_params(**kwargs):
    """
    Generate HTML attribute syntax from inputted keyword arguments.

    The output value is sorted by the passed keys, to provide consistent output
    each time this function is called with the same parameters. Because of the
    frequent use of the normally reserved keywords `class` and `for`, suffixing
    these with an underscore will allow them to be used.

    In order to facilitate the use of ``data-`` and ``aria-`` attributes, if the
    name of the attribute begins with ``data_`` or ``aria_``, then every
    underscore will be replaced with a hyphen in the generated attribute.

    >>> html_params(data_attr='user.name', aria_labeledby='name')
    'data-attr="user.name" aria-labeledby="name"'

    In addition, the values ``True`` and ``False`` are special:
      * ``attr=True`` generates the HTML compact output of a boolean attribute,
        e.g. ``checked=True`` will generate simply ``checked``
      * ``attr=False`` will be ignored and generate no output.

    >>> html_params(name='text1', id='f', class_='text')
    'class="text" id="f" name="text1"'
    >>> html_params(checked=True, readonly=False, name="text1", abc="hello")
    'abc="hello" checked name="text1"'

    .. versionchanged:: 3.0
        ``aria_`` args convert underscores to hyphens like ``data_``
        args.

    .. versionchanged:: 2.2
        ``data_`` args convert all underscores to hyphens, instead of
        only the first one.
    """
    params = []
    for k, v in sorted(kwargs.items()):
        k = clean_key(k)
        if v is True:
            params.append(k)
        elif v is False:
            pass
        else:
            v = escape(v).replace(Markup('"'), Markup("&quot;"))
            params.append(Markup('{k}="{v}"').format(k=k, v=v))
    return Markup(" ").join(params)


class ListWidget:
    """
    Render a list of fields as a :mdn-tag:`ul` or :mdn-tag:`ol`.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """

    def __init__(self, html_tag="ul", prefix_label=True):
        assert html_tag in ("ol", "ul")
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {html_params(**kwargs)}>"]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li>{subfield.label} {subfield()}</li>")
            else:
                html.append(f"<li>{subfield()} {subfield.label}</li>")
        html.append(f"</{self.html_tag}>")
        return Markup("".join(html))


class TableWidget:
    """
    Render a list of fields as a :mdn-tag:`table`.

    If `with_table_tag` is True, then an enclosing :mdn-tag:`table` is placed
    around the rows.

    Hidden fields will not be displayed with a row, instead the field will be
    pushed into a subsequent table row to ensure XHTML validity. Hidden fields
    at the end of the field list will appear outside the table.
    """

    def __init__(self, with_table_tag=True):
        self.with_table_tag = with_table_tag

    def __call__(self, field, **kwargs):
        html = []
        if self.with_table_tag:
            kwargs.setdefault("id", field.id)
            table_params = html_params(**kwargs)
            html.append(f"<table {table_params}>")
        hidden = ""
        for subfield in field:
            if subfield.type in ("HiddenField", "CSRFTokenField"):
                hidden += str(subfield)
            else:
                html.append(
                    f"<tr><th>{subfield.label}</th><td>{hidden}{subfield}</td></tr>"
                )
                hidden = ""
        if self.with_table_tag:
            html.append("</table>")
        if hidden:
            html.append(hidden)
        return Markup("".join(html))


class DataListWidget:
    """
    Render a :class:`~wtforms.DataList` as a :mdn-tag:`datalist` element.

    Used as the default widget for :class:`~wtforms.DataList`. Receives
    the bound :class:`~wtforms.DataList`, the current ``field`` (when
    rendered from a field), and any HTML attributes to apply to the
    ``<datalist>`` element. The DataList's ``render_kw`` is merged with
    the caller's keyword arguments — caller kwargs win, and the
    DataList's ``id`` always wins over both.
    """

    def __call__(self, datalist, field=None, **kwargs):
        render_kw = {clean_key(k): v for k, v in datalist.render_kw.items()}
        kwargs = {clean_key(k): v for k, v in kwargs.items()}
        attrs = {**render_kw, "id": datalist.id, **kwargs}
        options = []
        for choice in datalist.iter_choices(field):
            option_attrs = {"value": choice.value}
            if choice.label is not None and choice.label != choice.value:
                option_attrs["label"] = choice.label
            if choice.render_kw:
                option_attrs = {**choice.render_kw, **option_attrs}
            options.append(f"<option {html_params(**option_attrs)}>")
        return Markup(f"<datalist {html_params(**attrs)}>{''.join(options)}</datalist>")


class Input:
    """
    Render a basic :mdn-tag:`input` field.

    This is used as the basis for most of the other input fields.

    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.
    """

    html_params = staticmethod(html_params)

    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        datalist = getattr(field, "_datalist", None)
        if datalist is not None and "list" not in kwargs:
            kwargs["list"] = datalist if isinstance(datalist, str) else datalist.id
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                value = getattr(flags, k)
                kwargs[k] = value() if callable(value) else value
        input_params = self.html_params(name=field.name, **kwargs)
        return Markup(f"<input {input_params}>")


class Button:
    """
    Render a ``<button>`` element.

    Pass ``label=`` when rendering to override the visible button text. The
    label is HTML-escaped; pass a :class:`markupsafe.Markup` instance to embed
    HTML (icons, formatted text) in the button content.
    """

    html_params = staticmethod(html_params)
    input_type = "submit"
    validation_attrs = ["disabled"]

    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def __call__(self, field, **kwargs):
        label = kwargs.pop("label", field.label.text)
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        kwargs.setdefault("value", field._value())
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        button_params = self.html_params(name=field.name, **kwargs)
        return Markup(f"<button {button_params}>{escape(label)}</button>")


class TextInput(Input):
    """
    Render a single-line :mdn-input:`text`.
    """

    input_type = "text"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class PasswordInput(Input):
    """
    Render an :mdn-input:`password`.

    For security purposes, this field will not reproduce the value on a form
    submit by default. To have the value filled in, set `hide_value` to
    `False`.
    """

    input_type = "password"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def __call__(self, field, **kwargs):
        if self.hide_value:
            kwargs["value"] = ""
        return super().__call__(field, **kwargs)


class HiddenInput(Input):
    """
    Render an :mdn-input:`hidden`.
    """

    input_type = "hidden"
    validation_attrs = ["disabled"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_flags = {"hidden": True}


class CheckboxInput(Input):
    """
    Render an :mdn-input:`checkbox`.

    The ``checked`` HTML attribute is set if the field's data is a non-false value.
    """

    input_type = "checkbox"
    validation_attrs = ["required", "disabled"]

    def __call__(self, field, **kwargs):
        if getattr(field, "checked", field.data):
            kwargs.setdefault("checked", True)
        return super().__call__(field, **kwargs)


class RadioInput(Input):
    """
    Render a single :mdn-input:`radio` button.

    This widget is most commonly used in conjunction with ListWidget or some
    other listing, as singular radio buttons are not very useful.
    """

    input_type = "radio"
    validation_attrs = ["required", "disabled"]

    def __call__(self, field, **kwargs):
        if field.checked:
            kwargs.setdefault("checked", True)
        return super().__call__(field, **kwargs)


class FileInput(Input):
    """Render an :mdn-input:`file`.

    :param multiple: allow choosing multiple files
    """

    input_type = "file"
    validation_attrs = ["required", "disabled", "accept"]

    def __init__(self, multiple=False):
        super().__init__()
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        # browser ignores value of file input for security
        kwargs["value"] = False

        if self.multiple:
            kwargs["multiple"] = True

        return super().__call__(field, **kwargs)


class SubmitInput(Input):
    """
    Renders an :mdn-input:`submit`.

    The field's label is used as the text of the submit button instead of the
    data on the field.
    """

    input_type = "submit"
    validation_attrs = ["required", "disabled"]

    def __call__(self, field, **kwargs):
        kwargs.setdefault("value", field.label.text)
        return super().__call__(field, **kwargs)


class TextArea:
    """
    Renders a multi-line :mdn-tag:`textarea`.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """

    validation_attrs = ["required", "disabled", "readonly", "maxlength", "minlength"]

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        textarea_params = html_params(name=field.name, **kwargs)
        textarea_innerhtml = escape(field._value())
        return Markup(
            f"<textarea {textarea_params}>\r\n{textarea_innerhtml}</textarea>"
        )


class Select:
    """
    Renders a :mdn-tag:`select` field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield :class:`Choice`.
    """

    validation_attrs = ["required", "disabled"]

    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if self.multiple:
            kwargs["multiple"] = True
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        select_params = html_params(name=field.name, **kwargs)
        html = [f"<select {select_params}>"]
        render = type(self)._dispatch_render_option()
        if field.has_groups():
            for optgroup, choices in field._iter_groups_normalized():
                if optgroup is not None:
                    optgroup_params = html_params(label=optgroup)
                    html.append(f"<optgroup {optgroup_params}>")
                for choice in choices:
                    html.append(render(choice))
                if optgroup is not None:
                    html.append("</optgroup>")
        else:
            for choice in field._iter_choices_normalized():
                html.append(render(choice))
        html.append("</select>")
        return Markup("".join(html))

    @classmethod
    def render_option(cls, choice, **kwargs):
        value = choice.value
        if isinstance(value, bool):
            value = str(value)
        options = {"value": value, **(choice.render_kw or {}), **kwargs}
        if choice.selected:
            options["selected"] = True
        label = escape(choice.value if choice.label is None else choice.label)
        return Markup(f"<option {html_params(**options)}>{label}</option>")

    @classmethod
    def _dispatch_render_option(cls):
        """Return a callable ``(choice) -> str`` that invokes :meth:`render_option`.

        Picks the right signature for the override.
        """
        ro = cls.render_option
        try:
            sig = get_signature(ro)
        except (ValueError, TypeError):
            return ro
        positional_required = [
            p
            for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            and p.default is p.empty
        ]
        if len(positional_required) <= 1:
            return ro
        warnings.warn(
            f"{cls.__module__}.{cls.__qualname__}.render_option uses the "
            "pre-3.3 signature (value, label, selected, **kwargs). Override "
            "render_option(cls, choice, **kwargs) instead — choice is a "
            "SelectChoice. The legacy signature will be removed in WTForms "
            "4.0.",
            DeprecationWarning,
            stacklevel=3,
        )
        accepts_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())

        def adapter(choice):
            label = choice.value if choice.label is None else choice.label
            args = (choice.value, label, choice.selected)
            if accepts_kwargs:
                return ro(*args, **(choice.render_kw or {}))
            return ro(*args)

        return adapter


class Option:
    """
    Render an individual :mdn-tag:`option` from a select field.

    This is just a convenience for various custom rendering situations, and an
    option by itself does not constitute an entire field.
    """

    def __call__(self, field, **kwargs):
        return Select.render_option(field.choice, **kwargs)


class SearchInput(Input):
    """
    Render an :mdn-input:`search`.
    """

    input_type = "search"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class TelInput(Input):
    """
    Render an :mdn-input:`tel`.
    """

    input_type = "tel"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class URLInput(Input):
    """
    Render an :mdn-input:`url`.
    """

    input_type = "url"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class EmailInput(Input):
    """
    Render an :mdn-input:`email`.
    """

    input_type = "email"
    validation_attrs = [
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    ]


class _DateTimeBaseInput(Input):
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]

    def __call__(self, field, **kwargs):
        format = getattr(field, "format", None)
        if format is not None:
            format = format[0] if isinstance(format, list) else format
            flags = getattr(field, "flags", {})
            for attr in ("min", "max"):
                value = kwargs.get(attr, getattr(flags, attr, None))
                if callable(value):
                    value = value()
                if hasattr(value, "strftime"):
                    kwargs[attr] = value.strftime(format)
        return super().__call__(field, **kwargs)


class DateTimeInput(_DateTimeBaseInput):
    """
    Render an ``<input type="datetime">`` control.

    This is a legacy HTML input type. For modern browser support, prefer
    :class:`DateTimeLocalInput`.
    """

    input_type = "datetime"


class DateInput(_DateTimeBaseInput):
    """
    Render a :mdn-input:`date`.
    """

    input_type = "date"


class MonthInput(_DateTimeBaseInput):
    """
    Render an :mdn-input:`month`.
    """

    input_type = "month"


class WeekInput(_DateTimeBaseInput):
    """
    Render an :mdn-input:`week`.
    """

    input_type = "week"


class TimeInput(_DateTimeBaseInput):
    """
    Render a :mdn-input:`time`.
    """

    input_type = "time"


class DateTimeLocalInput(_DateTimeBaseInput):
    """
    Render an :mdn-input:`datetime-local`.
    """

    input_type = "datetime-local"


class NumberInput(Input):
    """
    Render an :mdn-input:`number`.
    """

    input_type = "number"
    validation_attrs = ["required", "disabled", "readonly", "max", "min", "step"]

    def __init__(self, step=None, min=None, max=None):
        self.step = step
        self.min = min
        self.max = max

    def __call__(self, field, **kwargs):
        if self.step is not None:
            kwargs.setdefault("step", self.step)
        if self.min is not None:
            kwargs.setdefault("min", self.min)
        if self.max is not None:
            kwargs.setdefault("max", self.max)
        return super().__call__(field, **kwargs)


class RangeInput(NumberInput):
    """
    Render an :mdn-input:`range`.
    """

    input_type = "range"
    validation_attrs = ["disabled", "max", "min", "step"]


class ColorInput(Input):
    """
    Render an :mdn-input:`color`.
    """

    input_type = "color"
    validation_attrs = ["disabled"]
