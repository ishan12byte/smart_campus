import pytest

from app.jwt_utils import create_access_token, decode_access_token


def test_access_token_creation_and_decoding():
    token = create_access_token(123)

    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert "exp" in payload


def test_invalid_token_is_rejected():
    with pytest.raises(ValueError):
        decode_access_token("this-is-not-a-valid-token")