from app.security import hash_password, verify_password


def test_password_is_hashed():
    password = "MySecurePassword123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_wrong_password_is_rejected():
    password = "MySecurePassword123"

    hashed = hash_password(password)

    assert not verify_password("WrongPassword123", hashed)