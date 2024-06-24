import pytest

from wtforms.validators import url
from wtforms.validators import ValidationError


@pytest.mark.parametrize(
    "url_val",
    [
        "http://foobar.dk",
        "http://foobar.dk/",
        "http://foo-bar.dk/",
        "http://foo--bar.dk/",
        "http://foo_bar.dk/",
        "http://foobar.dk?query=param",
        "http://foobar.dk/path?query=param",
        "http://foobar.dk/path?query=param&foo=faa",
        "http://foobar.museum/foobar",
        "http://192.168.0.1/foobar",
        "http://192.168.0.1:9000/fake",
        "http://\u0645\u062b\u0627\u0644."
        "\u0625\u062e\u062a\u0628\u0627\u0631/foo.com",  # Arabic
        "http://उदाहरण.परीक्षा/",  # Hindi
        "http://실례.테스트",  # Hangul
        "http://username:password@foobar.dk",
        "http://username@foobar.dk",
        "http://usern@me:p@ssword@foobar.dk",
        "http://username:password@foobar.dk:1234/path?query=parm",
    ],
)
def test_valid_url_passes(url_val, dummy_form, dummy_field):
    """
    Valid url should pass without raising
    """
    validator = url()
    dummy_field.data = url_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "url_val",
    [
        "http://localhost/foobar",
        "http://foobar",
        "http://foobar?query=param&foo=faa",
        "http://foobar:5000?query=param&foo=faa",
        "http://foobar/path?query=param&foo=faa",
        "http://foobar:1234/path?query=param&foo=faa",
        "http://user:password@foobar:1234/path?query=param&foo=faa",
    ],
)
def test_valid_url_notld_passes(url_val, dummy_form, dummy_field):
    """
    Require TLD option set to false, correct URL should pass without raising
    """
    validator = url(require_tld=False)
    dummy_field.data = url_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "url_val",
    [
        "http://foobar",
        "http://-foobar.dk/",
        "http://foobar-.dk/",
        "foobar.dk",
        "http://127.0.0/asdf",
        "http://foobar.d",
        "http://foobar.12",
        "http://localhost:abc/a",
    ],
)
def test_bad_url_raises(url_val, dummy_form, dummy_field):
    """
    Bad url should raise ValidationError
    """
    validator = url()
    dummy_field.data = url_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)
