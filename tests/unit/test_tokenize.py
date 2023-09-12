from experiment import tokenize


def test_get_tokens():
    assert tokenize.get_tokens("Test text", lower=True) == ["test", "text"]
    assert tokenize.get_tokens("Test text", lower=False) == ["Test", "text"]

    assert tokenize.get_tokens("Test.", lower=False) == ["Test", "."]
    assert tokenize.get_tokens("Test.", lower=False, remove_nonalphanumeric_tokens=True) == ["Test"]
