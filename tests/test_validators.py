import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.validators import is_valid_email, is_strong_password, require_fields

def test_valid_emails():
    assert is_valid_email("viky@gmail.com")       is True
    assert is_valid_email("v.iky+tag@uni.edu.eg") is True

def test_invalid_emails():
    assert is_valid_email("notanemail")    is False
    assert is_valid_email("missing@")     is False
    assert is_valid_email("@nodomain.com") is False

def test_strong_password():
    assert is_strong_password("Test1234")  is True
    assert is_strong_password("abcDEF99")  is True

def test_weak_password():
    assert is_strong_password("short1")    is False  # too short
    assert is_strong_password("allletter") is False  # no digit
    assert is_strong_password("12345678")  is False  # no letter

def test_require_fields_all_present():
    missing = require_fields({"a": 1, "b": 2}, ["a", "b"])
    assert missing == []

def test_require_fields_some_missing():
    missing = require_fields({"a": 1}, ["a", "b", "c"])
    assert set(missing) == {"b", "c"}

def test_require_fields_empty_value():
    missing = require_fields({"a": "", "b": "val"}, ["a", "b"])
    assert "a" in missing
