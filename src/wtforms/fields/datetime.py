import datetime
import warnings
from collections.abc import Callable

from wtforms import widgets
from wtforms.fields.core import Field
from wtforms.utils import clean_datetime_format_for_strptime

__all__ = (
    "DateTimeField",
    "DateField",
    "TimeField",
    "MonthField",
    "DateTimeLocalField",
    "WeekField",
)


class DateTimeField(Field):
    """
    A text field which stores a :class:`datetime.datetime` matching one or
    several formats. If ``format`` is a list, any input value matching any
    format will be accepted, and the first format in the list will be used
    to produce HTML values.

    .. deprecated:: 3.2.3
       ``DateTimeField`` renders ``<input type="datetime">``, which is
       obsolete. Use :class:`DateTimeLocalField` instead. ``DateTimeField``
       will be removed in WTForms 3.4.
    """

    widget = widgets.DateTimeInput()

    def __init__(
        self,
        label=None,
        validators=None,
        format="%Y-%m-%d %H:%M:%S",
        invalid_value_message=None,
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        if type(self) is DateTimeField:
            warnings.warn(
                "'DateTimeField' renders <input type=\"datetime\">, which is"
                " obsolete. Use 'DateTimeLocalField' instead. 'DateTimeField'"
                " will be removed in WTForms 3.4.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.format = format if isinstance(format, list) else [format]
        self.strptime_format = clean_datetime_format_for_strptime(self.format)
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Not a valid datetime value."
        )

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        if not self.data:
            return ""
        format = self.format[0]
        # data=/obj may supply a plain string; still render for the widget.
        if not hasattr(self.data, "strftime"):
            return str(self.data)
        return self.data.strftime(format)

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.datetime.strptime(date_str, format)
                return
            except ValueError:
                self.data = None

        raise ValueError(self.invalid_value_message)


class DateField(DateTimeField):
    """
    Same as :class:`~wtforms.fields.DateTimeField`, except stores a
    :class:`datetime.date` and renders as an :mdn-input:`date`.
    """

    widget = widgets.DateInput()

    def __init__(
        self,
        label=None,
        validators=None,
        format="%Y-%m-%d",
        invalid_value_message=None,
        **kwargs,
    ):
        super().__init__(
            label,
            validators,
            format,
            invalid_value_message=invalid_value_message,
            **kwargs,
        )
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Not a valid date value."
        )

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.datetime.strptime(date_str, format).date()
                return
            except ValueError:
                self.data = None

        raise ValueError(self.invalid_value_message)


class TimeField(DateTimeField):
    """
    Same as :class:`~wtforms.fields.DateTimeField`, except stores a
    :class:`datetime.time` and renders as an :mdn-input:`time`.
    """

    widget = widgets.TimeInput()

    def __init__(
        self,
        label=None,
        validators=None,
        format="%H:%M",
        invalid_value_message=None,
        **kwargs,
    ):
        super().__init__(
            label,
            validators,
            format,
            invalid_value_message=invalid_value_message,
            **kwargs,
        )
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Not a valid time value."
        )

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        time_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.datetime.strptime(time_str, format).time()
                return
            except ValueError:
                self.data = None

        raise ValueError(self.invalid_value_message)


class MonthField(DateField):
    """
    Same as :class:`~wtforms.fields.DateField`, except represents a month,
    stores a :class:`datetime.date` with `day = 1`, and renders as an
    :mdn-input:`month`.
    """

    widget = widgets.MonthInput()

    def __init__(self, label=None, validators=None, format="%Y-%m", **kwargs):
        super().__init__(label, validators, format, **kwargs)


class WeekField(DateField):
    """
    Same as :class:`~wtforms.fields.DateField`, except represents a week,
    stores a :class:`datetime.date` of the monday of the given week, and
    renders as an :mdn-input:`week`.
    """

    widget = widgets.WeekInput()

    def __init__(
        self,
        label=None,
        validators=None,
        format="%Y-W%W",
        invalid_value_message=None,
        **kwargs,
    ):
        super().__init__(
            label,
            validators,
            format,
            invalid_value_message=invalid_value_message,
            **kwargs,
        )
        self.invalid_value_message = invalid_value_message or self.gettext(
            "Not a valid week value."
        )

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        time_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                if "%w" not in format:
                    # The '%w' week starting day is needed. This defaults it to monday
                    # like ISO 8601 indicates.
                    self.data = datetime.datetime.strptime(
                        f"{time_str}-1", f"{format}-%w"
                    ).date()
                else:
                    self.data = datetime.datetime.strptime(time_str, format).date()
                return
            except ValueError:
                self.data = None

        raise ValueError(self.invalid_value_message)


class DateTimeLocalField(DateTimeField):
    """
    Same as :class:`~wtforms.fields.DateTimeField`, but represents an
    :mdn-input:`datetime-local`.

    :param tz:
        Optional timezone associated with the input. The HTML
        ``datetime-local`` widget always renders and submits a naive
        local datetime; ``tz`` declares the zone in which that local
        datetime should be interpreted. Accepts:

        - ``None`` (default): legacy behavior, :attr:`data` is naive.
        - a :class:`datetime.tzinfo` instance: parsed values get this
          zone attached, and aware values rendered through the field
          are converted to it before being formatted.
        - a callable returning a :class:`datetime.tzinfo` (or ``None``):
          resolved on each access, useful when the zone depends on the
          request context (e.g. user preferences). Returning ``None``
          falls back to the naive behavior.

        No correction is applied for DST gaps or overlaps — submitted
        values are annotated as-is via ``replace(tzinfo=...)``.
    """

    widget = widgets.DateTimeLocalInput()

    def __init__(
        self,
        *args,
        tz: datetime.tzinfo | Callable[[], datetime.tzinfo | None] | None = None,
        **kwargs,
    ):
        kwargs.setdefault(
            "format",
            [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%dT%H:%M",
            ],
        )
        super().__init__(*args, **kwargs)
        self.tz = tz

    def _resolve_tz(self):
        return self.tz() if callable(self.tz) else self.tz

    def _value(self):
        """Render :attr:`data`, converting aware values to ``tz`` and stripping
        the zone before formatting."""
        if self.raw_data:
            return " ".join(self.raw_data)

        if not self.data:
            return ""

        value = self.data
        if not hasattr(value, "strftime"):
            return str(value)
        tz = self._resolve_tz()
        if tz is not None and getattr(value, "tzinfo", None) is not None:
            value = value.astimezone(tz).replace(tzinfo=None)

        return value.strftime(self.format[0])

    def process_formdata(self, valuelist):
        """Parse the submitted value and annotate it with ``tz`` if set."""
        super().process_formdata(valuelist)
        tz = self._resolve_tz()
        if tz is not None and self.data is not None:
            self.data = self.data.replace(tzinfo=tz)
