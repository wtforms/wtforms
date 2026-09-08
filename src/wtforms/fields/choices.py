import warnings
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from itertools import groupby
from operator import attrgetter
from typing import NamedTuple

from wtforms import widgets
from wtforms._compat import get_signature
from wtforms.fields.core import Field
from wtforms.validators import ValidationError

__all__ = (
    "SelectField",
    "Choice",
    "SelectChoice",
    "SelectMultipleField",
    "RadioField",
)


class Choice(NamedTuple):
    """
    A rendered option yielded by
    :meth:`SelectFieldBase.iter_choices` and
    :meth:`SelectFieldBase.iter_groups`.

    ``selected`` is computed against the field's current data. To
    declare options on a :class:`SelectField`, use
    :class:`SelectChoice` instead.

    :param value:
        The value that will be sent in the request.
    :param label:
        The label of the option.
    :param selected:
        Whether the option is currently selected. Set by ``iter_choices``;
        you rarely set this yourself.
    :param render_kw:
        A dict containing HTML attributes that will be rendered
        with the option.
    """

    value: str
    label: str
    selected: bool
    render_kw: dict


@dataclass
class SelectChoice:
    """
    An option declared via :class:`SelectField` and
    :class:`SelectMultipleField`'s ``choices=`` parameter.

    :param value:
        The value that will be sent in the request.
    :param label:
        The label of the option. Defaults to ``value`` when omitted.
    :param render_kw:
        A dict containing HTML attributes that will be rendered
        with the option. Defaults to an empty dict when omitted.
    :param optgroup:
        The ``<optgroup>`` HTML tag in which the option will be rendered.
    """

    value: str
    label: str = None  # type: ignore[assignment]
    render_kw: dict = field(default_factory=dict)
    optgroup: str | None = None

    def __post_init__(self):
        if self.label is None:
            self.label = self.value

    def __iter__(self):
        return iter((self.value, self.label, self.render_kw, self.optgroup))

    @classmethod
    def from_input(cls, input, optgroup=None):
        """Coerce a value passed by the user via ``choices=...`` into a
        :class:`SelectChoice`.
        """
        if isinstance(input, SelectChoice):
            if optgroup:
                return replace(input, optgroup=optgroup)
            return input

        if isinstance(input, Choice):
            warnings.warn(
                "Passing Choice to a SelectField is deprecated; Choice is the "
                "output type returned by iter_choices(). Use SelectChoice "
                "instead. Support for Choice as input will be removed in "
                "WTForms 4.0.",
                DeprecationWarning,
                stacklevel=4,
            )
            return cls(
                value=input.value,
                label=input.label,
                render_kw=input.render_kw,
                optgroup=optgroup,
            )

        if isinstance(input, str):
            return cls(value=input, optgroup=optgroup)

        if isinstance(input, tuple):
            if len(input) not in (2, 3):
                raise ValueError(
                    f"SelectField choice tuple must have 2 or 3 elements, "
                    f"got {len(input)}"
                )
            return cls(*input, optgroup=optgroup)


def _enum_options(enum_cls, by, label, factory):
    if by not in ("value", "name"):
        raise ValueError(f"by must be 'value' or 'name', got {by!r}")
    if label is None:
        label = str if "__str__" in enum_cls.__dict__ else lambda m: m.name
    return [factory(value=getattr(m, by), label=label(m)) for m in enum_cls]


def enum_choices(enum_cls, *, by="value", label=None):
    """Build a list of :class:`SelectChoice` from an :class:`enum.Enum` class.

    ``by`` selects which member attribute becomes the HTML ``value=``:
    ``"value"`` (the default) emits ``member.value``, ``"name"`` emits
    ``member.name``. Use ``"name"`` for enums whose values are not good
    transport identifiers (non-string, non-unique or non-serialisable).

    The label defaults to ``str(member)`` when the Enum defines its own
    ``__str__``, otherwise to ``member.name``. Pass ``label=`` (a callable
    taking a member) to override.

    Pair with :func:`enum_coerce` using the same ``by`` to round-trip the
    submitted string back into a member.
    """
    return _enum_options(enum_cls, by, label, SelectChoice)


def enum_coerce(enum_cls, *, by="value"):
    """Return a ``coerce`` callable mapping a submitted string back to an
    :class:`enum.Enum` member.

    ``by`` must match the one passed to :func:`enum_choices`: ``"value"``
    (the default) resolves ``str(member.value)`` — so ``IntEnum`` values
    round-trip too — and ``"name"`` resolves ``member.name``. Already-coerced
    members pass through unchanged.
    """
    if by not in ("value", "name"):
        raise ValueError(f"by must be 'value' or 'name', got {by!r}")

    def coerce(v):
        if isinstance(v, enum_cls):
            return v

        try:
            if by == "value":
                by_value = {str(m.value): m for m in enum_cls}
                return by_value[str(v)]
            else:
                return enum_cls[v]
        except KeyError as e:
            raise ValueError(str(e)) from e

    return coerce


def _normalize_iter_choice(choice):
    """Coerce a value yielded by :meth:`SelectFieldBase.iter_choices` or
    :meth:`SelectFieldBase.iter_groups` into a :class:`Choice`.
    """
    if isinstance(choice, Choice):
        return choice
    if isinstance(choice, tuple):
        warnings.warn(
            "Yielding raw tuples from iter_choices() or iter_groups() is "
            "deprecated; yield Choice instances instead. Will be removed "
            "in WTForms 4.0.",
            DeprecationWarning,
            stacklevel=3,
        )
        if len(choice) == 4:
            value, label, selected, render_kw = choice
        elif len(choice) == 3:
            value, label, selected = choice
            render_kw = {}
        else:
            raise TypeError(
                f"iter_choices()/iter_groups() yielded a tuple of unsupported "
                f"length: {len(choice)}"
            )
        return Choice(value=value, label=label, selected=selected, render_kw=render_kw)
    raise TypeError(
        f"iter_choices()/iter_groups() yielded an unsupported type: "
        f"{type(choice).__name__}"
    )


class SelectFieldBase(Field):
    option_widget = widgets.Option()

    """
    Base class for fields which can be iterated to produce options.

    This isn't a field, but an abstract base class for fields which want to
    provide this functionality.
    """

    def __init__(self, label=None, validators=None, option_widget=None, **kwargs):
        super().__init__(label, validators, **kwargs)

        if option_widget is not None:
            self.option_widget = option_widget

    def iter_choices(self):
        """Provide data for choice widget rendering.

        Should yield :class:`Choice` instances.
        """
        raise NotImplementedError()

    def _iter_choices_normalized(self):
        """Wrap :meth:`iter_choices` to always yield :class:`Choice`."""
        for choice in self.iter_choices():
            yield _normalize_iter_choice(choice)

    def has_groups(self):
        """Whether the field's choices include any ``optgroup`` hint."""
        return False

    def iter_groups(self):
        """Yield ``(group_label, [Choice, ...])`` pairs for grouped rendering."""
        raise NotImplementedError()

    def _iter_groups_normalized(self):
        """Wrap :meth:`iter_groups` to always yield ``(name, [Choice, ...])``."""
        for name, group in self.iter_groups():
            yield name, [_normalize_iter_choice(c) for c in group]

    def __iter__(self):
        opts = dict(
            widget=self.option_widget,
            validators=self.validators,
            name=self.name,
            render_kw=self.render_kw,
            _form=self._form,
            _meta=self.meta,
        )
        for i, choice in enumerate(self._iter_choices_normalized()):
            opt = self._Option(
                id=f"{self.id}-{i}",
                label=choice.value if choice.label is None else choice.label,
                **opts,
            )
            opt.choice = choice
            opt.checked = choice.selected
            opt.process(None, choice.value)
            yield opt

    def _choices_from_input(self, choices):
        """Parse the user-supplied ``choices`` into a list of :class:`SelectChoice`."""
        if callable(choices):
            choices = self._invoke_choices_callback(choices)

        if choices is None:
            return None

        if isinstance(choices, dict):
            if self._is_shorthand_dict(choices):
                result = []
                for key, value in choices.items():
                    if isinstance(value, dict):
                        for inner_value, inner_label in value.items():
                            result.append(
                                SelectChoice(
                                    value=inner_value, label=inner_label, optgroup=key
                                )
                            )
                    else:
                        result.append(SelectChoice(value=key, label=value))
                return result
            return [
                SelectChoice.from_input(input, optgroup)
                for optgroup, inputs in choices.items()
                for input in inputs
            ]

        return [SelectChoice.from_input(input) for input in choices]

    @staticmethod
    def _is_shorthand_dict(choices):
        """``True`` if ``choices`` matches the shorthand dict syntax.

        Shorthand is ``dict[str, str | dict[str, str]]``.
        """
        return all(isinstance(v, (str, dict)) for v in choices.values())

    @staticmethod
    def _warn_legacy_choices(choices):
        """Emit a one-shot ``DeprecationWarning`` for legacy ``choices`` shapes.

        Legacy shapes are raw tuples or ``dict``.
        """
        if isinstance(choices, dict):
            if SelectFieldBase._is_shorthand_dict(choices):
                return
            warnings.warn(
                "Passing SelectField choices in a dict is deprecated and will be "
                "removed in wtforms 3.4. Please pass a list of SelectChoice "
                "objects with a custom optgroup attribute instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            items = (i for v in choices.values() for i in v)
        else:
            items = choices
        for item in items:
            if isinstance(item, (SelectChoice, Choice)):
                continue
            if isinstance(item, tuple):
                warnings.warn(
                    "Passing SelectField choices as tuples is deprecated and "
                    "will be removed in wtforms 3.4. Please use SelectChoice "
                    "instead.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                return

    def _invoke_choices_callback(self, cb):
        try:
            sig = get_signature(cb)
        except (ValueError, TypeError):
            return cb()
        try:
            sig.bind(self._form, self)
        except TypeError:
            return cb()
        return cb(self._form, self)

    class _Option(Field):
        def _value(self):
            return str(self.data)


class SelectField(SelectFieldBase):
    widget = widgets.Select()

    def __init__(
        self,
        label=None,
        validators=None,
        coerce=str,
        choices=None,
        validate_choice=True,
        invalid_value_message=None,
        invalid_choice_message=None,
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        self.coerce = coerce
        if callable(choices):
            self._choices_callable = choices
            self.choices = None
        else:
            self._choices_callable = None
            if choices is None:
                self.choices = None
            else:
                self._warn_legacy_choices(choices)
                self.choices = (
                    dict(choices) if isinstance(choices, dict) else list(choices)
                )
        self.validate_choice = validate_choice
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Invalid Choice: could not coerce."
        )
        self.invalid_choice_message = invalid_choice_message or self.gettext(
            "Not a valid choice."
        )

    def iter_choices(self):
        choices = self._choices_from_input(self.choices) or []
        return [
            Choice(
                value=c.value,
                label=c.label,
                selected=self.coerce(c.value) == self.data,
                render_kw=c.render_kw,
            )
            for c in choices
        ]

    def has_groups(self):
        choices = self._choices_from_input(self.choices) or []
        return any(c.optgroup is not None for c in choices)

    def iter_groups(self):
        choices = self._choices_from_input(self.choices) or []
        for optgroup, group in groupby(choices, key=attrgetter("optgroup")):
            yield (
                optgroup,
                [
                    Choice(
                        value=c.value,
                        label=c.label,
                        selected=self.coerce(c.value) == self.data,
                        render_kw=c.render_kw,
                    )
                    for c in group
                ],
            )

    def post_process(self, formdata=None):
        super().post_process(formdata)
        if self._choices_callable is not None:
            self.choices = self._invoke_choices_callback(self._choices_callable)

    def process_data(self, value):
        try:
            # If value is None, don't coerce to a value
            self.data = self.coerce(value) if value is not None else None
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        try:
            self.data = self.coerce(valuelist[0])
        except ValueError as exc:
            raise ValueError(self.invalid_value_message) from exc

    def pre_validate(self, form):
        if self.process_errors:
            return

        if not self.validate_choice:
            return

        if self.choices is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        if not any(choice.selected for choice in self._iter_choices_normalized()):
            raise ValidationError(self.invalid_choice_message)


class SelectMultipleField(SelectField):
    """
    No different from a normal select field, except this one can take (and
    validate) multiple choices. You'll need to specify the HTML
    :mdn-attr:`size` attribute on the :mdn-tag:`select` field when rendering.

    ``invalid_choice_message`` may be a string, or a callable taking the
    number of invalid submitted values and returning the message. The
    returned message must contain ``%(value)s``, which is replaced with the
    comma-separated list of unacceptable values.
    """

    widget = widgets.Select(multiple=True)

    def __init__(
        self,
        label=None,
        validators=None,
        coerce=str,
        choices=None,
        validate_choice=True,
        invalid_value_message=None,
        invalid_choice_message=None,
        **kwargs,
    ):
        super().__init__(
            label,
            validators,
            coerce=coerce,
            choices=choices,
            validate_choice=validate_choice,
            **kwargs,
        )
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Invalid choice(s): one or more data inputs could not be coerced."
        )
        self.invalid_choice_message = invalid_choice_message

    def iter_choices(self):
        choices = self._choices_from_input(self.choices) or []
        data = self.data or ()
        return [
            Choice(
                value=c.value,
                label=c.label,
                selected=self.coerce(c.value) in data,
                render_kw=c.render_kw,
            )
            for c in choices
        ]

    def iter_groups(self):
        choices = self._choices_from_input(self.choices) or []
        data = self.data or ()
        for optgroup, group in groupby(choices, key=attrgetter("optgroup")):
            yield (
                optgroup,
                [
                    Choice(
                        value=c.value,
                        label=c.label,
                        selected=self.coerce(c.value) in data,
                        render_kw=c.render_kw,
                    )
                    for c in group
                ],
            )

    def process_data(self, value):
        try:
            self.data = list(self.coerce(v) for v in value)
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        try:
            self.data = list(self.coerce(x) for x in valuelist)
        except ValueError as exc:
            raise ValueError(self.invalid_value_message) from exc

    def pre_validate(self, form):
        if self.process_errors:
            return

        if not self.validate_choice or not self.data:
            return

        if self.choices is None:
            raise TypeError(self.gettext("Choices cannot be None."))

        acceptable = {
            self.coerce(choice.value) for choice in self._iter_choices_normalized()
        }
        if any(data not in acceptable for data in self.data):
            unacceptable = [
                str(data) for data in set(self.data) if data not in acceptable
            ]
            if callable(self.invalid_choice_message):
                message = self.invalid_choice_message(len(unacceptable))
            elif self.invalid_choice_message is not None:
                message = self.invalid_choice_message
            else:
                message = self.ngettext(
                    "'%(value)s' is not a valid choice for this field.",
                    "'%(value)s' are not valid choices for this field.",
                    len(unacceptable),
                )
            raise ValidationError(message % dict(value="', '".join(unacceptable)))


class RadioField(SelectField):
    """
    Like a SelectField, except displays a list of :mdn-input:`radio` buttons.

    Iterating the field will produce subfields (each containing a label as
    well) in order to allow custom rendering of the individual radio fields.
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.RadioInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.label.field_id = False
