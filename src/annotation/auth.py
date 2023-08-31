def generate_auth_token() -> str:
    import binascii
    import os

    auth_token = binascii.b2a_hex(os.urandom(16)).decode("ascii")
    return auth_token


def cast_unicode(s: bytes | str, encoding: str) -> str:
    if isinstance(s, bytes):
        return s.decode(encoding, "replace")
    return s


def passwd_hash(passphrase: str) -> str:
    from argon2 import PasswordHasher

    ph = PasswordHasher(
        memory_cost=10240,
        time_cost=10,
        parallelism=8,
    )
    h = ph.hash(passphrase)

    return ":".join(("argon2", cast_unicode(h, "ascii")))


def passwd_check(hashed_passphrase: str, passphrase: str) -> bool:
    # modification of source provided with a BSD 3-Clause License, Copyright (c) 2015-, Jupyter Development Team
    # from notebook.auth.security
    assert hashed_passphrase.startswith("argon2:")
    import argon2
    import argon2.exceptions

    ph = argon2.PasswordHasher()
    try:
        return ph.verify(hashed_passphrase[7:], passphrase)
    except argon2.exceptions.VerificationError:
        return False
