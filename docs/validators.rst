Validators
==========
.. module:: wtforms.validators

A validator simply takes an input, verifies it fulfills some criterion, such as
a maximum length for a string and returns. Or, if the validation fails, raises
a :class:`~wtforms.validators.ValidationError`. This system is very simple and
flexible, and allows you to chain any number of validators on fields.

.. autoclass:: wtforms.validators.ValidationError
.. autoclass:: wtforms.validators.StopValidation

Built-in validators
-------------------

.. autoclass:: wtforms.validators.DataRequired

   This also sets the ``required`` :attr:`flag <wtforms.fields.Field.flags>` on
   fields it is used on. This flag causes the ``required`` attribute to be
   rendered in the tag, which prevents a request/response cycle for validation.
   This behavior can be overridden in the following ways:

   -   Specifying ``required=False`` when rendering in the template.
   -   Making a custom a widget that doesn't set it.
   -   Rendering the ``novalidate`` attribute" on the ``form`` tag, or the
       ``formnovalidate`` attribute on a submit button.

   The ``required`` flag behavior also applies to the :class:`InputRequired` class.

.. autoclass:: wtforms.validators.Email

.. autoclass:: wtforms.validators.EqualTo

    This validator can be used to facilitate in one of the most common
    scenarios, the password change form::

        class ChangePassword(Form):
            password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
            confirm  = PasswordField('Repeat Password')

    In the example, we use the InputRequired validator to prevent the EqualTo
    validator from trying to see if the passwords do not match if there was no
    passwords specified at all. Because InputRequired stops the validation chain,
    EqualTo is not run in the case the password field is left empty.

.. autoclass:: wtforms.validators.InputRequired

   This also sets the ``required`` :attr:`flag <wtforms.fields.Field.flags>` on
   fields it is used on. See :class:`DataRequired` for a description of behavior
   regarding this flag.

.. autoclass:: wtforms.validators.IPAddress

.. autoclass:: wtforms.validators.Length

.. autoclass:: wtforms.validators.MacAddress

.. autoclass:: wtforms.validators.NumberRange

.. autoclass:: wtforms.validators.DateRange

    This validator can be used with a custom callback to make it somewhat dynamic::

        from datetime import date
        from datetime import datetime
        from datetime import timedelta
        from functools import partial

        from wtforms import Form
        from wtforms.fields import DateField
        from wtforms.fields import DateTimeLocalField
        from wtforms.validators import DateRange


        def in_n_days(days):
            return datetime.now() + timedelta(days=days)


        cb = partial(in_n_days, 5)


        class DateForm(Form):
            date = DateField("date", [DateRange(min=date(2023, 1, 1), max_callback=cb)])
            datetime = DateTimeLocalField(
                "datetime-local",
                [
                    DateRange(
                        min=datetime(2023, 1, 1, 15, 30),
                        max_callback=cb,
                        input_type="datetime-local",
                    )
                ],
            )

    In the example, we use the DateRange validator to prevent a date outside of a
    specified range. for the field ``date`` we set the minimum range statically,
    but the date must not be newer than the current time + 5 days. For the field
    ``datetime`` we do the same, but specify an input_type to achieve the correct
    formatting for the corresponding field type.


.. autoclass:: wtforms.validators.Optional

   This also sets the ``optional`` :attr:`flag <wtforms.fields.Field.flags>` on
   fields it is used on.


.. autoclass:: wtforms.validators.Regexp

.. autoclass:: wtforms.validators.URL

.. autoclass:: wtforms.validators.UUID

.. autoclass:: wtforms.validators.AnyOf

.. autoclass:: wtforms.validators.NoneOf

.. autoclass:: wtforms.validators.ReadOnly

.. autoclass:: wtforms.validators.Disabled

.. _custom-validators:

Custom validators
-----------------

We will step through the evolution of writing a length-checking validator
similar to the built-in :class:`Length` validator, starting from a
case-specific one to a generic reusable validator.

Let's start with a simple form with a name field and its validation::

    class MyForm(Form):
        name = StringField('Name', [InputRequired()])

        def validate_name(form, field):
            if len(field.data) > 50:
                raise ValidationError('Name must be less than 50 characters')

Above, we show the use of an :ref:`in-line validator <inline-validators>` to do
validation of a single field. In-line validators are good for validating
special cases, but are not easily reusable.  If, in the example above, the
`name` field were to be split into two fields for first name and surname, you
would have to duplicate your work to check two lengths.

So let's start on the process of splitting the validator out for re-use::

    def my_length_check(form, field):
        if len(field.data) > 50:
            raise ValidationError('Field must be less than 50 characters')

    class MyForm(Form):
        name = StringField('Name', [InputRequired(), my_length_check])

All we've done here is move the exact same code out of the class and as a
function. Since a validator can be any callable which accepts the two
positional arguments form and field, this is perfectly fine, but the validator
is very special-cased.

Instead, we can turn our validator into a more powerful one by making it a
factory which returns a callable::

    def length(min=-1, max=-1):
        message = 'Must be between %d and %d characters long.' % (min, max)

        def _length(form, field):
            l = field.data and len(field.data) or 0
            if l < min or max != -1 and l > max:
                raise ValidationError(message)

        return _length

    class MyForm(Form):
        name = StringField('Name', [InputRequired(), length(max=50)])

Now we have a configurable length-checking validator that handles both minimum
and maximum lengths. When ``length(max=50)`` is passed in your validators list,
it returns the enclosed `_length` function as a closure, which is used in the
field's validation chain.

This is now an acceptable validator, but we recommend that for reusability, you
use the pattern of allowing the error message to be customized via passing a
``message=`` parameter:

.. code-block:: python

    class Length(object):
        def __init__(self, min=-1, max=-1, message=None):
            self.min = min
            self.max = max
            if not message:
                message = 'Field must be between %i and %i characters long.' % (min, max)
            self.message = message

        def __call__(self, form, field):
            l = field.data and len(field.data) or 0
            if l < self.min or self.max != -1 and l > self.max:
                raise ValidationError(self.message)

    length = Length

In addition to allowing the error message to be customized, we've now converted
the length validator to a class. This wasn't necessary, but we did this to
illustrate how one would do so. Because fields will accept any callable as a
validator, callable classes are just as applicable. For complex validators, or
using inheritance, you may prefer this.

We aliased the ``Length`` class back to the original ``length`` name in the
above example. This allows you to keep API compatibility as you move your
validators from factories to classes, and thus we recommend this for those
writing validators they will share.


Setting flags on the field with validators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, it's useful to know if a validator is present on a given field, like
for use in template code. To do this, validators are allowed to specify flags
which will then be available on the :attr:`field's flags object
<wtforms.fields.Field.flags>`.  Some of the built-in validators such as
:class:`Required` already do this.

To specify flags on your validator, set the ``field_flags`` attribute on your
validator. When the Field is constructed, the flags with the same name will be
set on your field. For example, let's imagine a validator that
validates that input is valid BBCode. We can set a flag on the field then to
signify that the field accepts BBCode::

    # class implementation
    class ValidBBCode(object):
        def __init__(self):
            self.field_flags = {'accepts_bbcode': True}

    # factory implementation
    def valid_bbcode():
        def _valid_bbcode(form, field):
            pass # validator implementation here

        _valid_bbcode.field_flags = {'accepts_bbcode': True}
        return _valid_bbcode

Then we can check it in our template, so we can then place a note to the user:

.. code-block:: html+jinja

    {{ field(rows=7, cols=70) }}
    {% if field.flags.accepts_bbcode %}
        <div class="note">This field accepts BBCode formatting as input.</div>
    {% endif %}

Some considerations on using flags:

* Boolean flags will set HTML valueless attributes (e.g. `{required: True}`
  will give `<input type="text" required>`). Other flag types will set regular
  HTML attributes (e.g. `{maxlength: 8}` will give `<input type="text" maxlength="8">`).
* If multiple validators set the same flag, the flag will have the value set
  by the first validator.
* Flags are set from validators only in :meth:`Field.__init__`, so inline
  validators and extra passed-in validators cannot set them.
