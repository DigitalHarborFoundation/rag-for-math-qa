import pytest


@pytest.fixture(autouse=True)
def no_openai(monkeypatch):
    """Remove Embedding and ChatCompletion creations during all RAG unit tests.

    It's not actually clear to me that this works."""
    monkeypatch.delattr("openai.Embedding.create")
    monkeypatch.delattr("openai.ChatCompletion.create")
