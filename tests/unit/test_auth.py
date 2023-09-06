from experiment import auth


def test_passwd_check():
    passphrase = "test"
    hashed_passphrase = auth.passwd_hash(passphrase)
    assert auth.passwd_check(hashed_passphrase, passphrase)
