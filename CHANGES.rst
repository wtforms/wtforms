.. currentmodule:: wtforms

Version 3.X.X
-------------

Unreleased

- :class:`~validators.URL` validator is based on `urllib.urlparse` and
  allows `username:password@` values.

Version 3.1.2
-------------

Released 2024-01-06

- Fix :class:`~fields.SelectMultipleField` value coercion on validation.
  :issue:`822` :pr:`823`

Version 3.1.1
-------------

Released 2023-11-01

- Display :class:`~wtforms.Flags` values in their repr. :pr:`808`
- :class:`~fields.SelectField` and :class:`~fields.SelectMultipleField`
  ``choices`` can be `None` if `validate_choice` is `False` :pr:`809`
- Documentation improvements :pr:`812` :pr:`815` :pr:`817`
- Unit tests improvements :pr:`813`
- Python 3.12 support :pr:`818`
- Restored support for 3-items tuple return value from `iter_choices`
  :pr:`816`


Version 3.1.0
-------------

Released 2023-10-10

-   Documentation improvements :pr:`726` :pr:`733` :pr:`749`
    :pr:`767` :pr:`788` :pr:`789` :pr:`793`
-   Translation improvements :pr:`732` :pr:`734` :pr:`754`
-   Implement :class:`~fields.ColorField` :pr:`755`
-   Delayed import of ``email_validator``. :issue:`727`
-   ``<option>`` attributes can be passed by the :class:`~fields.SelectField`
    ``choices`` parameter :issue:`692` :pr:`739`.
    ⚠️breaking change⚠️: `iter_choices` now returns a tuple of 4 items
-   Use the standard datetime formats by default for
    :class:`~fields.DateTimeLocalField`  :pr:`761`
-   Python 3.11 support :pr:`763`
-   Added shorter format to :class:`~fields.DateTimeLocalField`
    defaults :pr:`761`
-   Stop support for python 3.7 :pr:`794`
-   Added shorter format to :class:`~fields.WeekField`
    defaults :pr:`765`
-   Move to pyproject.toml :pr:`796`
-   URL validator takes a ``allow_ip`` parameter :pr:`800`
-   Implement :class:`~validators.ReadOnly` and
    :class:`~validators.Disabled` `:pr:`788`

Version 3.0.1
-------------

Released 2021-12-23

-   Fixed :class:`~fields.DateTimeField` and other similar fields can
    handle multiple formats. :issue:`720` :pr:`721`
-   Stop support for python 3.6 :pr:`722`

Version 3.0.0
-------------

Released 2021-11-07

-   Fixed :class:`~fields.RadioField` validators. :issue:`477` :pr:`615`
-   :meth:`~fields.FormField.populate_obj` always calls :func:`setattr`
    :pr:`675`
-   WTForms has a new logo. :issue:`569` :pr:`689`
-   Fixed :class:`~fields.RadioField` `render_kw` rendering. :issue:`490`
    :pr:`628` :pr:`688`
-   Support for optgroups in :class:`~fields.SelectField` and
    :class:`~fields.SelectMultipleField`. :issue:`656` :pr:`667`
-   Minor documentation fix. :issue:`701`
-   Custom separators for :class:`~fields.FieldList`. :issue:`681` :pr:`694`
-   :class:`~fields.DateTimeField`, :class:`~fields.DateField` and
    :class:`~fields.TimeField` support time formats that removes leading
    zeros. :pr:`703`
-   Refactoring: split `fields/core.py` and `fields/simple.py` :pr:`710`

Version 3.0.0a1
---------------

Released 2020-11-23

-   Drop support for Python < 3.6. :pr:`554`
-   :class:`~fields.StringField` sets ``data`` to ``None`` when form
    data is empty and an initial value was not provided. Although it
    previously set an empty string, ``None`` is consistent with the
    behavior of other fields. :pr:`355`
-   Specified version of Babel required for setup to avoid errors.
    :pr:`430`
-   Replaced use of ``getattr``/``setattr`` with regular variable
    access. :issue:`482`
-   :class:`ValueError` raised by a validator are handled like regular
    exceptions. Validators need to raise
    :class:`~validators.ValidationError` or
    :class:`~validators.StopValidation` to make a validation fail.
    :issue:`445`
-   :class:`~fields.SelectField`, :class:`~fields.SelectMultipleField` and
    :class:`~fields.RadioField` *choices* parameter can be a callable.
    :pr:`608`
-   Choices shortcut for :class:`~fields.core.SelectMultipleField`.
    :issue:`603` :pr:`605`
-   Forms can have form-level errors. :issue:`55` :pr:`595`
-   Implemented :class:`~wtforms.fields.core.MonthField`. :pr:`530` :pr:`593`
-   Filters can be inline. :meth:`form.BaseForm.process` takes a
    *extra_filters* parameter. :issue:`128` :pr:`592`
-   Fields can be passed the ``name`` argument to use a HTML name
    different than their Python name. :issue:`205`, :pr:`601`
-   Render attribute names like ``for_`` and ``class_`` are normalized
    consistently so later values override those specified earlier.
    :issue:`449`, :pr:`596`
-   Flags should now be stored in dicts and can take non-boolean values.
    A ``DeprecationWarning`` is issued when tuples are used. :issue:`406` :pr:`467`
-   Widgets are HTML5 by default. :issue:`594` :pr:`614`
-   Fixed a bug when the :class:`~wtforms.fields.core.SelectField` choices
    are list of strings. :pr:`598`
-   Error messages standardization. :issue:`613` :pr:`620` :pr:`626` :pr:`627`
-   :class:`~wtforms.fields.core.SelectMultipleField` `validate_choice`
    bugfix. :issue:`606` :pr:`642`
-   Fixed SelectMultipleField validation when using choices list shortcut.
    :issue:`612` :pr:`661`
-   Removed :meth:`form._get_translations`. Use
    :meth:`Meta.get_translations <wtforms.meta.DefaultMeta.get_translations>` instead.


Version 2.3.3
-------------

Released 2020-07-30

-   This release includes the translation files that were missing in the
    2.3.2 release. :issue:`641`


Version 2.3.2
-------------

Released 2020-07-29

-   Fixed a bug with :class:`~fields.SelectField` choices shortcut at
    form submission. :pr:`598, 639`


Version 2.3.1
-------------

Released 2020-04-22

-   All modules in ``wtforms.ext`` show a deprecation warning on import.
    They will be removed in version 3.0.
-   Fixed a bug when :class:`~fields.SelectField` choices is ``None``.
    :issue:`572, 585`
-   Restored ``HTMLString`` and ``escape_html`` as aliases for
    MarkupSafe functions. Their use shows a ``DeprecationWarning``.
    :issue:`581`, :pr:`583`
-   ``Form.validate`` takes an ``extra_validators`` parameter, mapping
    field names to lists of extra validator functions. This matches
    ``BaseForm.validate``. :pr:`584`
-   Update locale catalogs.


Version 2.3.0
-------------

Released 2020-04-21

-   Drop support for Python 2.6, 3.3, and 3.4.
-   :class:`~fields.SelectField` uses ``list()`` to construct a new list
    of choices. :pr:`475`
-   Permitted underscores in ``HostnameValidation``. :pr:`463`
-   :class:`~validators.URL` validator now allows query parameters in
    the URL. :issue:`523`, :pr:`524`
-   Updated ``false_values`` param in ``BooleanField`` docs.
    :issue:`483`, :pr:`485`
-   Fixed broken format string in Arabic translation :pr:`471`
-   Updated French and Japanese translations. :pr:`506, 514`
-   Updated Ukrainian translation. :pr:`433`
-   ``FieldList`` error list keeps entries in order for easier
    identification of which fields had errors. :issue:`257`, :pr:`407`
-   :class:`~validators.Length` gives a more helpful error message when
    ``min`` and ``max`` are the same value. :pr:`266`
-   :class:`~fields.SelectField` no longer coerces ``None`` to
    ``"None"`` allowing use of ``"None"`` as an option. :issue:`289`,
    :pr:`288`
-   The :class:`~widgets.TextArea` widget prepends a ``\r\n`` newline
    when rendering to account for browsers stripping an initial line for
    display. This does not affect the value. :issue:`238`, :pr:`395`
-   HTML5 :class:`~fields.html5.IntegerField` and
    :class:`~fields.html5.RangeInput` don't render the ``step="1"``
    attribute by default. :pr:`343`
-   ``aria_`` args are rendered the same way as ``data_`` args, by
    converting underscores to hyphens. ``aria_describedby="name-help"``
    becomes ``aria-describedby="name-help"``. :issue:`239`, :pr:`389`
-   Added a ``check_validators`` method to :class:`~fields.Field` which
    checks if the given validators are both callable, and not classes.
    :pr:`298, 410`
-   ``form.errors`` is not cached and will update if an error is
    appended to a field after access. :pr:`568`
-   :class:`~wtforms.validators.NumberRange` correctly handle NaN
    values. :issue:`505`, :pr:`548`
-   :class:`~fields.IntegerField` checks input type when processing
    data. :pr:`451`
-   Added a parameter to :class:`~fields.SelectField` to skip choice
    validation. :issue:`434`, :pr:`493`
-   Choices which name and data are the same do not need to use tuples.
    :pr:`526`
-   Added more documentation on HTML5 fields. :pr:`326, 409`
-   HTML is escaped using MarkupSafe instead of the previous internal
    implementation. :func:`~widgets.core.escape_html` is removed,
    replaced by :func:`markupsafe.escape`.
    :class:`~widgets.core.HTMLString` is removed, replaced by
    :class:`markupsafe.Markup`. :pr:`400`
-   Fixed broken IPv6 validator, validation now uses the ``ipaddress``
    package. :issue:`385`, :pr:`403`
-   :class:`~fields.core.Label` text is escaped before rendering.
    :issue:`315`, :pr:`375`
-   Email validation is now handled by an optional library,
    ``email_validator``. :pr:`429`


Version 2.2.1
-------------

Released 2018-06-07

-   :class:`~fields.StringField` only sets ``data = ''`` when form data
    is empty and an initial value was not provided. This fixes an issue
    where the default value wasn't rendered with the initial form.
    :issue:`291, 401`, :pr:`355`


Version 2.2
-----------

Released 2018-06-02

-   Merged new and updated translations from the community.
-   Passing ``data_`` args to render a field converts all the
    underscores to hyphens when rendering the HTML attribute, not just
    the first one. ``data_foo_bar`` becomes ``data-foo-bar``. :pr:`248`
-   The :class:`~validators.UUID` validator uses the :class:`uuid.UUID`
    class instead of a regex. :pr:`251`
-   :class:`~fields.SelectField` copies the list of ``choices`` passed
    to it so modifying an instance's choices will not modify the global
    form definition. :pr:`286`
-   Fields call :meth:`~fields.Field.process_formdata` even if the raw
    data is empty. :pr:`280`
-   Added a :class:`~fields.MultipleFileField` to handle a multi-file
    input. :class:`~fields.FileField` continues to handle only one
    value. The underlying :class:`~widgets.FileInput` widget gained a
    ``multiple`` argument. :pr:`281`
-   :class:`~fields.SelectField` choices can contain HTML (MarkupSafe
    ``Markup`` object or equivalent API) and will be rendered properly.
    :pr:`302`
-   ``fields.TimeField`` and ``html5.TimeField`` were added. :pr:`254`
-   Improved :class:`~validators.Email`. Note that it is still
    unreasonable to validate all emails with a regex and you should
    prefer validating by actually sending an email. :pr:`294`
-   Widgets render the ``required`` attribute when using a validator
    that provides the ``'required'`` flag, such as
    :class:`~validators.DataRequired`. :pr:`361`
-   Fix a compatibility issue with SQLAlchemy 1.2 that caused
    :class:`~ext.sqlalchemy.fields.QuerySelectField` to fail with
    ``ValueError: too many values to unpack``. :pr:`391`


Version 2.1
-----------

Released 2015-12-15

-   Added ``render_kw`` to allow default rendering time options.
-   Updated / added a number of localizations.
-   Updated docs.
-   Allow widgets to set flags.


Version 2.0.2
-------------

Released 2015-01-18

-   Added more localizations and updated some.
-   Validators for email and URL can validate IDNA-encoded domain names
    and new TLDs.
-   Better ``DeprecationWarnings``.
-   Support localization files in ``/usr/share/locale`` for distro
    packaging.


Version 2.0.1
-------------

Released 2014-07-01

-   Update wheel install to conditionally install ordereddict for Python
    2.6.
-   Doc improvements.


Version 2.0
-----------

Released 2014-05-20

-   Add new ``class Meta`` paradigm for much more powerful customization
    of WTForms.
-   Move i18n into core. Deprecate ``wtforms.ext.i18n``.
-   Move CSRF into core. Deprecate ``wtforms.ext.csrf``.
-   Fix issue rendering SelectFields with ``value=True``.
-   Make ``DecimalField`` able to use babel locale-based number
    formatting.
-   Drop Python 3.2 support (Python3 support for 3.3+ only).
-   Passing ``attr=False`` to WTForms widgets causes the value to be
    ignored.
-   ``Unique`` validator in ``wtforms.ext.sqlalchemy`` has been removed.
-   Deprecate ``form._get_translations``. Use ``Meta.get_translations`` instead.


Version 1.0.5
-------------

Released 2013-09-10

-   Fix a bug in validators which causes translations to happen once
    then clobber any future translations.
-   ``ext.sqlalchemy`` and ``ext.appengine`` minor cleanups /
    deprecation.
-   Allow blank string and the string ``false`` to be considered false
    values for ``BooleanField`` (configurable). This is technically a
    breaking change, but it is not likely to affect the majority of
    users adversely.
-   ``ext.i18n`` form allows passing ``LANGUAGES`` to the constructor.


Version 1.0.4
-------------

Released 2013-04-28

-   Add widgets and field implementations for HTML5 specialty input
    types.
-   ``ext.appengine`` add NDB support.
-   Add translations for Korean, Traditional Chinese.


Version 1.0.3
-------------

Released 2013-01-24

-   Tests complete in python 3.2/3.3.
-   Localization for ru, fr.
-   Minor fixes in documentation for clarity.
-   ``FieldList`` now can take validators on the entire ``FieldList``.
-   Fix issue with ``ext.sqlalchemy`` ``QuerySelectField``.
-   Fix issue in ``ext.sqlalchemy`` ``ColumnDefault`` conversion.
-   ``ext.sqlalchemy`` supports ``Enum`` type.
-   Field class now allows traversal in Django 1.4 templates.


Version 1.0.2
-------------

Released 2012-08-24

-   We now support Python 2.x and 3.x on the same codebase, thanks to a
    lot of hard work by Vinay Sajip.
-   Add in ability to convert relationships to ``ext.sqlalchemy``
    ``model_form``.
-   Built-in localizations for more languages.
-   Distinguish ``Required`` validator into ``InputRequired`` and
    ``DataRequired``.
-   Better IP address validation, including IPv6 support.
-   ``AnyOf`` / ``NoneOf`` now work properly formatting other datatypes
    than strings.
-   ``Optional`` validator can optionally pass through whitespace.


Version 1.0.1
-------------

Released 2012-02-29

-   Fixed issues related to building for Python 3 and Python
    pre-releases.
-   Add ``object_data`` to fields to get at the originally passed data.


Version 1.0
-----------

Released 2012-02-28

-   Output HTML5 compact syntax by default.
-   Substantial code reorg, cleanup, and test improvements.
-   Added ``ext.csrf`` for a way to implement CSRF protection.
-   ``ext.sqlalchemy`` supports ``PGInet``, ``MACADDR``, and ``UUID``
    field conversion.
-   ``ext.sqlalchemy`` supports callable defaults.
-   ``ext.appengine`` ``model_form`` now supports generating forms with
    the same ordering as model.
-   ``ext.appengine`` ``ReferencePropertyField`` now gets ``get_label``
    like the other ORM fields.
-   Add localization support for WTForms built-in messages.
-   Python 3 support (via 2to3).
-   An empty label string can be specified on fields if desired.
-   ``Option`` widget can now take kwargs customization.
-   Field subclasses can provide default validators as a class property.
-   ``DateTimeField`` can take time in microseconds.
-   Numeric fields all set ``.data`` to ``None`` on coercion error for
    consistency.


Version 0.6.3
-------------

Released 2011-04-24

-   Documentation: Substantial documentation improvements, including
    adding Crash Course as a Sphinx document.
-   ``ext.django`` ``QuerySetSelectField`` and ``ModelSelectField`` now
    accept ``get_label`` similar to sqlalchemy equivalents.
-   ``ext.appengine`` ``model_form`` fixes for  ``FloatField``,
    ``TimeField``, and ``DateTimeField``.
-   ``ext.appengine`` ``ReferencePropertyField`` now properly stores
    model object, not key.


Version 0.6.2
-------------

Released 2011-01-22

-   ``ext.appengine`` various field fixes.
-   ``ext.appengine`` ``model_form`` changes.
-   Fix issue in ``Optional`` with non-string input.
-   Make numeric fields more consistent.
-   Improve test coverage substantially.


Version 0.6.1
-------------

Released 2010-09-17

-   ``ext.appengine`` ``ReferencePropertyField``.
-   Dateutil fields render issue, and consistency issue.
-   ``Optional`` validator failed when ``raw_data`` was absent
-   Documentation: docs now mention HTML escaping functionality.
-   Add preliminary support for providing a translations object that can
    translate built-in validation and coercion errors.


Version 0.6
-----------

Released 2010-04-25

-   HTML is now marked as safe (using ``__html__``) so that compatible
    templating engines will not auto-escape it.
-   ``Field._default`` is now ``Field.default``.
-   All fields now have a ``raw_data`` property.
-   Fields which are select fields (including those in ``.ext``) can be
    iterated to produce options, and have an ``option_widget`` kwarg.
-   Minor bugfixes and cleanup in ``FieldList``,
    ``Select(Multiple)Field``, ``QuerySelectField`` to address
    behavioral consistency.
-   Added ``FloatField``, based on ``IntegerField``.
-   ``ext.appengine`` now supports ``FloatProperty`` and
    ``GeoPtProperty``.
-   ``ext.sqlalchemy`` ``QueryMultipleSelectField`` changed to
    ``QuerySelectMultipleField``.


Version 0.5
-----------

Released 2010-02-13

-   Added a ``BaseForm`` class which provides the core processing and
    validation functionality of ``Form`` without requiring declarative
    subclassing.
-   Field labels now default to a humanized field name.
-   Fields now have a ``short_name`` property which is the un-prefixed
    name.
-   ``DecimalField`` now rounds values for display without float
    coercion. See docs for details on how to format decimals.
-   ``ext.sqlalchemy.fields`` now has an additional
    ``QuerySelectMultipleField``, and all fields can now support
    multiple-column primary keys.
-   ``ext.sqlalchemy.orm`` contains tools for making forms from ORM
    models.
-   Added ``ext.dateutil`` for flexible date-time parsing.
-   Added ``ext.appengine`` contributed by Rodrigo Moraes.
-   Added ``AnyOf`` and ``NoneOf`` validators.


Version 0.4
-----------

Released 2009-10-10

-   Fields have much greater control over input processing. Filters have
    been added to implement a simple way to transform input data.
-   Added fields that encapsulate advanced data structures such as
    dynamic lists or child forms for more powerful field composing.
-   Fields now use widgets for rendering.
-   All built-in validators have been converted to classes to clean up
    the code.
-   ``Form.auto_populate`` and ``Field.populate`` were renamed to
    ``populate_obj`` to clarify that they populate another object, not
    the Form or Field. This is an API breaking change.
-   Dropped support for Python 2.3.


Version 0.3.1
-------------

Released 2009-01-24

-   Several fixes were made to the code and tests to make WTForms
    compatible with Python 2.3/2.4.
-   Form's properties can now be accessed via dictionary-style access
    such as ``form['author']``. This also has the intended effect of
    making variable lookups in Django templates more reliable.
-   Form and Field construction changes: Form now uses a metaclass to
    handle creating its ``_unbound_fields`` property, and Field
    construction now gives an instance of the new ``UnboundField`` class
    instead of using a partial function application. These are both
    internal changes and do not change the API.


Version 0.3
-----------

Released 2009-01-18

-   Fields are now responsible for their own validation, instead of
    mostly relying on ``Form``. There are also new ``pre_validate`` and
    ``post_validate`` hooks on subfields, adding a great deal of
    flexibility when dealing with field-level validation. Note that this
    is an API breaking change if you have any subfields that override
    ``Field.validate``. These will need to be updated to use the new
    hooks.
-   ``process_data`` no longer accepts the ``has_formdata`` parameter.
-   At form instantiation time, ``process_data`` will be called only
    once for each field. If a model object is provided which contains
    the property, then this value is used. Otherwise, a keyword argument
    if specified is used. Failing that, the field's default value is
    used.
-   If any form data is sent, ``process_formdata`` will be called after
    ``process_data`` for each field. If no form data is available for
    the given field, it is called with an empty list.
-   ``wtforms.ext.django`` has been overhauled, both to mirror features
    and changes of the Django 1.0 release, and to add some useful fields
    for working with Django ORM data in forms.
-   The ``checker`` keyword argument to ``SelectField``,
    ``SelectMultipleField``, and ``RadioField`` has been renamed to
    ``coerce`` to reflect the actual functionality of this callable.


Version 0.2
-----------

Released 2009-01-13

-   We have documentation and unit tests!
-   Fields now have a ``flags`` property which contain boolean flags
    that are set either by the field itself or validators being
    specified on a field. The flags can then be used in checks in
    template or Python code.
-   Changed the way fields take parameters, they are no longer quasi
    magic. This is a breaking change. Please see the documentation for
    the new syntax.
-   Added optional description argument to ``Field``, accessible on the
    field as ``description``. This provides an easy way to define e.g.
    help text in the same place as the form.
-   Added new semantics for validators which can stop the validation
    chain, with or without errors.
-   Added a regexp validator, and removed the ``not_empty`` validator in
    favour of two validators, optional and required. The new validators
    allow control over the validation chain in addition to checking
    emptiness.
-   Renamed ``wtforms.contrib`` to ``wtforms.ext`` and reorganised
    ``wtforms.ext.django``. This is a breaking change if you were using
    the Django extensions, but should only require changing your imports
    around a little.
-   Better support for other frameworks such as Pylons.


Version 0.1
-----------

Released 2008-07-25

-   Initial release.
