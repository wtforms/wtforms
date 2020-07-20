import decimal
import re

import pytest

from wtforms import Form
from wtforms import Label
from wtforms import StringField
from wtforms.validators import AnyOf
from wtforms.validators import data_required
from wtforms.validators import email
from wtforms.validators import equal_to
from wtforms.validators import input_required
from wtforms.validators import ip_address
from wtforms.validators import length
from wtforms.validators import mac_address
from wtforms.validators import network_address
from wtforms.validators import NoneOf
from wtforms.validators import NumberRange
from wtforms.validators import optional
from wtforms.validators import regexp
from wtforms.validators import StopValidation
from wtforms.validators import url
from wtforms.validators import UUID
from wtforms.validators import ValidationError


def test_data_required(dummy_form, dummy_field):
    """
    Should pass if the required data are present
    """
    validator = data_required()
    dummy_field.data = "foobar"
    validator(dummy_form, dummy_field)
    assert validator.field_flags == {"required": True}


@pytest.mark.parametrize("bad_val", [None, "", " ", "\t\t"])
def test_data_required_raises(bad_val, dummy_form, dummy_field):
    """
    data_required should stop the validation chain if data are not present
    """
    validator = data_required()
    dummy_field.data = bad_val
    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)


def test_data_required_clobber(dummy_form, dummy_field):
    """
    Data required should clobber the errors
    """
    validator = data_required()
    dummy_field.data = ""
    dummy_field.errors = ["Invalid Integer Value"]
    assert len(dummy_field.errors) == 1
    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)
        assert len(dummy_field.errors) == 0


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (data_required(), "This field is required."),
        (data_required(message="foo"), "foo"),
    ),
)
def test_data_required_messages(dummy_form, dummy_field, validator, message):
    """
    Check data_required message and custom message
    """
    dummy_field.data = ""

    with pytest.raises(StopValidation) as e:
        validator(dummy_form, dummy_field)
        assert str(e.value) == message


def test_input_required(dummy_form, dummy_field):
    """
    it should pass if the required value is present
    """
    validator = input_required()
    dummy_field.data = "foobar"
    dummy_field.raw_data = ["foobar"]

    validator(dummy_form, dummy_field)
    assert validator.field_flags == {"required": True}


def test_input_required_raises(dummy_form, dummy_field):
    """
    It should stop the validation chain if the required value is not present
    """
    validator = input_required()
    dummy_field.data = ""
    dummy_field.raw_data = [""]
    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (input_required(), "This field is required."),
        (input_required(message="foo"), "foo"),
    ),
)
def test_input_required_error_message(dummy_form, dummy_field, validator, message):
    """
    It should return error message when the required value is not present
    """
    dummy_field.data = ""
    dummy_field.raw_data = [""]

    with pytest.raises(StopValidation) as e:
        validator(dummy_form, dummy_field)
        assert str(e.value) == message


def test_input_optional_passes(dummy_form, dummy_field):
    """
    optional should pause with given values
    """
    validator = optional()
    dummy_field.data = "foobar"
    dummy_field.raw_data = ["foobar"]
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize("data_v, raw_data_v", [("", ""), ("   ", "   "), ("\t", "\t")])
def test_input_optional_raises(data_v, raw_data_v, dummy_form, dummy_field):
    """
    optional should stop the validation chain if the data are not given
    errors should be erased because the value is optional
    white space should be considered as empty string too
    """
    validator = optional()
    dummy_field.data = data_v
    dummy_field.raw_data = raw_data_v

    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)
        assert validator.field_flags == {"optional": True}

    dummy_field.errors = ["Invalid Integer Value"]
    assert len(dummy_field.errors) == 1

    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)
        assert len(dummy_field.errors) == 0


#############################################################


@pytest.mark.parametrize("address", ["147.230.23.25", "147.230.23.0", "127.0.0.1"])
def test_ip4address_passes(address, dummy_form, dummy_field):
    adr = ip_address()
    dummy_field.data = address
    adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address",
    [
        "2001:718:1C01:1111::1111",
        "2001:718:1C01:1111::",
        "::1",
        "dead:beef:0:0:0:0:42:1",
        "abcd:ef::42:1",
    ],
)
def test_good_ip6address_passes(address, dummy_form, dummy_field):
    adr = ip_address(ipv6=True)
    dummy_field.data = address
    adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address",
    [
        "2001:718:1C01:1111::1111",
        "2001:718:1C01:1111::",
        "abc.0.0.1",
        "abcd:1234::123::1",
        "1:2:3:4:5:6:7:8:9",
        "abcd::1ffff",
    ],
)
def test_bad_ip6address_raises(address, dummy_form, dummy_field):
    adr = ip_address()
    dummy_field.data = address
    with pytest.raises(ValidationError):
        adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address",
    [
        "147.230.1000.25",
        "2001:718::::",
        "abc.0.0.1",
        "1278.0.0.1",
        "127.0.0.abc",
        "900.200.100.75",
    ],
)
def test_bad_ip4address_raises(address, dummy_form, dummy_field):
    adr = ip_address(ipv6=True)
    dummy_field.data = address
    with pytest.raises(ValidationError):
        adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address", ["10.0.0.0/8", "172.16.0.0/16", "192.168.10.0/24"])
)
def test_network4address_passes(address, dummy_form, dummy_field):
    adr = network_address()
    dummy_field.data = address
    adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address", ["2001:db8:1234::/48", "2001:db8:a::/64"]
)
def test_good_network6address_passes(address, dummy_form, dummy_field):
    adr = network_address(ipv6=True)
    dummy_field.data = address
    adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address", ["2001:718:1C01:1111::1111", "2001:718:1C01:1111::", "abc.0.0.1"]
)
def test_bad_network6address_raises(address, dummy_form, dummy_field):
    adr = network_address()
    dummy_field.data = address
    with pytest.raises(ValidationError):
        adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "address", ["147.230.1000.25/24", "2001:718::::/64", "abc.0.0.1/33"]
)
def test_bad_network4address_raises(address, dummy_form, dummy_field):
    adr = network_address()
    dummy_field.data = address
    with pytest.raises(ValidationError):
        adr(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "email_address",
    ["foo@bar.dk", "123@bar.dk", "foo@456.dk", "foo@bar456.info", "foo@bücher.中国"],
)
def test_valid_email_passes(email_address, dummy_form, dummy_field):
    """
    Valid email address should pass without raising
    """
    validator = email()
    dummy_field.data = email_address
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "email_address",
    [
        None,
        "",
        "  ",
        "foo",
        "bar.dk",
        "foo@",
        "@bar.dk",
        "foo@bar",
        "foo@bar.ab12",
        "foo@.bar.ab",
        "foo.@bar.co",
        "foo@foo@bar.co",
        "fo o@bar.co",
    ],
)
def test_invalid_email_raises(email_address, dummy_form, dummy_field):
    """
    Bad email address should raise ValidationError
    """
    validator = email()
    dummy_field.data = email_address
    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)

    assert str(e.value) == "Invalid email address."


@pytest.mark.parametrize("email_address", ["foo@"])
def test_invalid_email_raises_granular_message(email_address, dummy_form, dummy_field):
    """
    When granular_message=True uses message from email_validator library.
    """
    validator = email(granular_message=True)
    dummy_field.data = email_address
    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)

    assert str(e.value) == "There must be something after the @-sign."


def test_ip_address_raises_on_bad_init():
    """
    IpAddress validator should raise ValueError when ipv6=False and ipv4=False
    """
    with pytest.raises(ValueError):
        ip_address(ipv4=False, ipv6=False)


@pytest.mark.parametrize("mac_addr_val", ["01:23:45:67:ab:CD"])
def test_valid_mac_passes(mac_addr_val, dummy_form, dummy_field):
    """
    Valid MAC address should pass without raising
    """
    validator = mac_address()
    dummy_field.data = mac_addr_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "mac_addr_val",
    ["00:00:00:00:00", "01:23:45:67:89:", "01:23:45:67:89:gh", "123:23:45:67:89:00"],
)
def test_bad_mac_raises(mac_addr_val, dummy_form, dummy_field):
    """
    Bad MAC address should raise ValidatioError
    """
    validator = mac_address()
    dummy_field.data = mac_addr_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "uuid_val",
    ["2bc1c94f-0deb-43e9-92a1-4775189ec9f8", "2bc1c94f0deb43e992a14775189ec9f8"],
)
def test_valid_uuid_passes(uuid_val, dummy_form, dummy_field):
    """
    Valid UUID should pass without raising
    """
    validator = UUID()
    dummy_field.data = uuid_val
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "uuid_val",
    [
        "2bc1c94f-deb-43e9-92a1-4775189ec9f8",
        "2bc1c94f-0deb-43e9-92a1-4775189ec9f",
        "gbc1c94f-0deb-43e9-92a1-4775189ec9f8",
        "2bc1c94f 0deb-43e9-92a1-4775189ec9f8",
    ],
)
def test_bad_uuid_raises(uuid_val, dummy_form, dummy_field):
    """
    Bad UUID should raise ValueError
    """
    validator = UUID()
    dummy_field.data = uuid_val
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_required_passes(dummy_form, dummy_field):
    """
    It should pass when required value is present
    """
    validator = data_required()
    dummy_field.data = "foobar"
    validator(dummy_form, dummy_field)


def test_required_stops_validation(dummy_form, dummy_field):
    """
    It should raise stop the validation chain if required value is not present
    """
    validator = data_required()
    dummy_field.data = ""
    with pytest.raises(StopValidation):
        validator(dummy_form, dummy_field)


def test_equal_to_passes(dummy_form, dummy_field):
    """
    Equal values should pass
    """
    dummy_field.data = "test"
    dummy_form["foo"] = dummy_field
    validator = equal_to("foo")
    validator(dummy_form, dummy_form["foo"])


@pytest.mark.parametrize(
    "field_val,equal_val", [("test", "invalid_field_name"), ("bad_value", "foo")]
)
def test_equal_to_raises(
    field_val, equal_val, dummy_form, dummy_field, dummy_field_class
):
    """
    It should raise ValidationError if the values are not equal
    """
    dummy_form["foo"] = dummy_field_class("test", label=Label("foo", "foo"))
    dummy_field.data = field_val
    validator = equal_to(equal_val)
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


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


@pytest.mark.parametrize("test_v, test_list", [("b", ["a", "b", "c"]), (2, [1, 2, 3])])
def test_anyof_passes(test_v, test_list, dummy_form, dummy_field):
    """
    it should pass if the test_v is present in the test_list
    """
    validator = AnyOf(test_list)
    dummy_field.data = test_v
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize("test_v, test_list", [("d", ["a", "b", "c"]), (6, [1, 2, 3])])
def test_anyof_raisses(test_v, test_list, dummy_form, dummy_field):
    """
    it should raise ValueError if the test_v is not present in the test_list
    """
    validator = AnyOf(test_list)
    dummy_field.data = test_v
    with pytest.raises(ValueError):
        validator(dummy_form, dummy_field)


def test_any_of_values_formatter(dummy_form, dummy_field):
    """
    Test AnyOf values_formatter formating of error message
    """

    def formatter(values):
        return "::".join(str(x) for x in reversed(values))

    validator = AnyOf([7, 8, 9], message="test %(values)s", values_formatter=formatter)
    dummy_field.data = 4
    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)
        assert str(e.value) == "test 9::8::7"


def test_none_of_passes(dummy_form, dummy_field):
    """
    it should pass if the value is not present in list
    """
    dummy_field.data = "d"
    validator = NoneOf(["a", "b", "c"])
    validator(dummy_form, dummy_field)


def test_none_of_raises(dummy_form, dummy_field):
    """
    it should raise ValueError if the value is present in list
    """
    dummy_field.data = "a"
    validator = NoneOf(["a", "b", "c"])
    with pytest.raises(ValueError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize("min_v, max_v", [(2, 6), (6, -1), (-1, 6), (6, 6)])
def test_correct_length_passes(min_v, max_v, dummy_form, dummy_field):
    """
    It should pass for the string with correct length
    """
    dummy_field.data = "foobar"
    validator = length(min_v, max_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize("min_v, max_v", [(7, -1), (-1, 5)])
def test_bad_length_raises(min_v, max_v, dummy_form, dummy_field):
    """
    It should raise ValidationError for string with incorect length
    """
    dummy_field.data = "foobar"
    validator = length(min_v, max_v)
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "min_v, max_v",
    [(-1, -1), (5, 2)],  # none of the values is specified  # max should be gt min
)
def test_bad_length_init_raises(min_v, max_v):
    """
    It should raise AssertionError if the validator constructor got wrong values
    """
    with pytest.raises(AssertionError):
        length(min_v, max_v)


@pytest.mark.parametrize(
    ("validator", "message"),
    (
        (length(2, 5, "%(min)d and %(max)d"), "2 and 5"),
        (length(8, -1), "at least 8"),
        (length(-1, 5), "longer than 5"),
        (length(2, 5), "between 2 and 5"),
        (length(5, 5), "exactly 5"),
    ),
)
def test_length_messages(dummy_form, dummy_field, validator, message):
    """
    It should raise ValidationError for string with incorect length
    """
    dummy_field.data = "foobar"

    with pytest.raises(ValidationError) as e:
        validator(dummy_form, dummy_field)
        assert str(e.value) == message


@pytest.mark.parametrize(
    "min_v, max_v, test_v", [(5, 10, 7), (5, None, 7), (None, 100, 70)]
)
def test_number_range_passes(min_v, max_v, test_v, dummy_form, dummy_field):
    """
    It should pass if the test_v is between min_v and max_v
    """
    dummy_field.data = test_v
    validator = NumberRange(min_v, max_v)
    validator(dummy_form, dummy_field)


@pytest.mark.parametrize(
    "min_v, max_v, test_v",
    [
        (5, 10, None),
        (5, 10, 0),
        (5, 10, 12),
        (5, 10, -5),
        (5, None, 4),
        (None, 100, 500),
    ],
)
def test_number_range_raises(min_v, max_v, test_v, dummy_form, dummy_field):
    """
    It should raise ValidationError if the test_v is not between min_v and max_v
    """
    dummy_field.data = test_v
    validator = NumberRange(min_v, max_v)
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


@pytest.mark.parametrize("nan", [float("NaN"), decimal.Decimal("NaN")])
def test_number_range_nan(nan, dummy_form, dummy_field):
    validator = NumberRange(0, 10)
    dummy_field.data = nan
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_lazy_proxy_raises(really_lazy_proxy):
    """
    Tests that the validators support lazy translation strings for messages.
    """
    with pytest.raises(Exception):
        str(really_lazy_proxy)


def test_lazy_proxy_fixture(really_lazy_proxy):
    """
    Tests that the validators support lazy translation strings for messages.
    """
    equal_to("fieldname", message=really_lazy_proxy)
    length(min=1, message=really_lazy_proxy)
    NumberRange(1, 5, message=really_lazy_proxy)
    data_required(message=really_lazy_proxy)
    regexp(".+", message=really_lazy_proxy)
    email(message=really_lazy_proxy)
    ip_address(message=really_lazy_proxy)
    url(message=really_lazy_proxy)


@pytest.mark.parametrize(
    "re_pattern, re_flags, test_v, expected_v",
    [
        ("^a", None, "abcd", "a"),
        ("^a", re.I, "ABcd", "A"),
        (re.compile("^a"), None, "abcd", "a"),
        (re.compile("^a", re.I), None, "ABcd", "A"),
    ],
)
def test_regex_passes(
    re_pattern, re_flags, test_v, expected_v, dummy_form, dummy_field
):
    """
    Regex should pass if there is a match.
    Should work for complie regex too
    """
    validator = regexp(re_pattern, re_flags) if re_flags else regexp(re_pattern)
    dummy_field.data = test_v
    assert validator(dummy_form, dummy_field).group(0) == expected_v


@pytest.mark.parametrize(
    "re_pattern, re_flags, test_v",
    [
        ("^a", None, "ABC"),
        ("^a", re.I, "foo"),
        ("^a", None, None),
        (re.compile("^a"), None, "foo"),
        (re.compile("^a", re.I), None, None),
    ],
)
def test_regex_raises(re_pattern, re_flags, test_v, dummy_form, dummy_field):
    """
    Regex should raise ValidationError if there is no match
    Should work for complie regex too
    """
    validator = regexp(re_pattern, re_flags) if re_flags else regexp(re_pattern)
    dummy_field.data = test_v
    with pytest.raises(ValidationError):
        validator(dummy_form, dummy_field)


def test_regexp_message(dummy_form, dummy_field, grab_error_message):
    """
    Regexp validator should return given message
    """
    validator = regexp("^a", message="foo")
    dummy_field.data = "f"
    assert grab_error_message(validator, dummy_form, dummy_field) == "foo"


@pytest.mark.parametrize("exc", [IndexError, ZeroDivisionError, ValueError])
def test_raise_exceptions(exc):
    def validate(form, field):
        raise exc

    class F(Form):
        field = StringField(validators=[validate])

    f = F()

    with pytest.raises(exc):
        f.validate()
