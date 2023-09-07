import string

import numpy as np
import pytest

from experiment import generate


def mock_get_completion(*args, **kwargs):
    choices = list(string.ascii_lowercase)
    return " ".join(np.random.choice(choices, size=50))


@pytest.fixture
def patch_get_completion(monkeypatch):
    monkeypatch.setattr(
        "experiment.generate.get_completion",
        mock_get_completion,
    )


def test_GenerationCorpus(tmp_path, patch_get_completion):
    corpus = generate.GenerationCorpus(tmp_path, "test_corpus1")
    assert len(corpus.generations) == 0
    messages = [
        {
            "role": "user",
            "content": "Test query",
        },
    ]
    metadata = {"test_key": "test_value"}
    assert corpus.generate(messages, metadata, sleep=0)
    assert not corpus.generate(messages, metadata, sleep=0)
    assert len(corpus.generations) == 1
    assert corpus.generations[0]["test_key"] == "test_value"
    assert corpus.generations[0]["generation"] is not None
    metadata = metadata.copy()  # NOTE: this will fail without a copy()!
    metadata["test_key"] = "test_value2"
    assert not corpus.is_already_generated(messages, metadata)
    assert corpus.generate(messages, metadata, sleep=0)
    assert len(corpus.generations) == 2
    assert corpus.generations[-1]["test_key"] == "test_value2"

    corpus2 = generate.GenerationCorpus(tmp_path, "test_corpus1")
    assert len(corpus2.generations) == 2
    assert corpus2.generations[0]["test_key"] == "test_value"
    assert corpus2.generations[-1]["test_key"] == "test_value2"
