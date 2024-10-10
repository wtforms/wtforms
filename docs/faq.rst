FAQ
===

This contains the most commonly asked questions about WTForms. The most current
version of this document can always be found on the `WTForms Website`_.

.. _WTForms Website: https://wtforms.readthedocs.io/


Does WTForms work with [library here]?
--------------------------------------

The answer is most likely **yes**. WTForms tries to provide as usable an API as
possible. We've listed here some of the known libraries to work with WTForms,
but if it's not listed, it doesn't mean it won't work.

* **Request/Form Input**

  * Django
  * Webob (Includes Pylons, Google App Engine, Turbogears)
  * Werkzeug (Includes Flask, Tipfy)
  * any other cgi.FieldStorage-type multidict

* **Templating Engines**

  * Jinja
  * Mako
  * Django Templates (To get the full power of WTForms in your templates, use
    `WTForms-Django`_.)
  * Genshi

* **Database Objects**

  * Pretty much any ORM or object-DB should work, as long as data objects allow
    attribute access to their members.

    Special support is there for `SQLAlchemy`_, `Google App Engine`_, and `Django`_
    collections via companion packages.

.. _SQLAlchemy: https://github.com/pallets-eco/wtforms-sqlalchemy
.. _Google App Engine: https://github.com/pallets-eco/wtforms-appengine
.. _WTForms-Django: https://github.com/pallets-eco/wtforms-django
.. _Django: https://github.com/pallets-eco/wtforms-django

Does WTForms support unicode?
-----------------------------

Simple answer: Yes.

Longer answer: WTForms uses unicode strings throughout the source code, and
assumes that form input has already been coerced to unicode by your framework
(Most frameworks already do this.) WTForms fields render to unicode strings by
default, and therefore as long as your templating engine can work with that,
you should have no unicode issues.


What versions of Python are supported?
--------------------------------------

WTForms supports Python 3.9+


How can I contribute to WTForms?
--------------------------------

WTForms is not that scary. Really. We try to keep it as succinct and readable as
possible. For bugs and feature requests, you can file a
ticket on the `project page`_.

.. _project page: https://github.com/pallets-eco/wtforms


How do I mark in a template when a field is required?
-----------------------------------------------------

Some validators (notably Required and Optional) set flags on the fields'
:attr:`~wtforms.fields.Field.flags` object. To use this in a template, you can
do something like:

.. code-block:: html+jinja

    {% for field in form %}
        {{ field }}
        {% if field.flags.required %}*{% endif %}{{ field.label }}
    {% endfor %}


Does WTForms handle file uploads?
---------------------------------

Currently, it does not. This is because WTForms strives to be
framework-agnostic, and every web framework handles file uploads somewhat
differently. WTForms has a :class:`~wtforms.fields.FileField` which will let
you render a file input widget, but the rest is up to you. An example use in a
django-ish framework::

    class MyForm(Form):
        image = FileField()

    def my_view(request):
        form = MyForm(request.POST)
        file_wrapper = request.FILES[form.image.name]
        # Do things with your file wrapper now

Using ``form.image.name`` is an easy way to know what input name was generated
for your file input, even if the form is prefixed.


Why does blank input not go back to the default value?
------------------------------------------------------

A key design decision of WTForms was that form data -always- takes precedence
when there's a form submission. That is, if a field exists on a form, and a
form was posted, but that field's value was missing, it will not revert to a
default, but instead store an empty value (and in some cases cause a validation
error.)

This is for a number of reasons:

1. Security. If a form reverted to defaults on missing data, then an evil user
   could potentially cause problems by submitting a hand-coded form with key
   missing fields.

2. Bug-finding. If you omitted a field in your template, it might fall through
   to the default and you'd possibly miss it.

3. Consistency.


How do I... [convoluted combination of libraries]
-------------------------------------------------

You'll probably want to check out our :doc:`specific_problems` doc.
