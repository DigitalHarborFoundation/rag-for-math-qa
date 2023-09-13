import string

import numpy as np
import pytest

from experiment import generate


def mock_get_completion(*args, **kwargs):
    choices = list(string.ascii_lowercase)
    return " ".join(np.random.choice(choices, size=50))


def mock_get_completion_error(*args, **kwargs):
    raise ValueError(f"Args: {args}")


@pytest.fixture
def patch_get_completion(monkeypatch):
    monkeypatch.setattr(
        "experiment.completion_utils.get_completion",
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


def test_GenerationCorpus_batch(tmp_path):
    corpus = generate.GenerationCorpus(tmp_path, "test_corpus")
    assert len(corpus.generations) == 0
    messages = [
        {
            "role": "user",
            "content": "Test query",
        },
    ]
    n_to_generate = 200
    metadata_list = [{"test_id": i, "messages": messages} for i in range(n_to_generate)]
    n_generated = corpus.batch_generate(
        metadata_list,
        n_processes=4,
        sleep=0,
        completion_func=mock_get_completion,
    )
    assert n_generated == n_to_generate, f"Expected {n_generated} generations, but only produced {n_to_generate}"
    assert len(corpus.generations) == n_to_generate
    for generation in corpus.generations:
        assert generation["generation"] is not None

    assert (
        corpus.batch_generate(
            metadata_list,
            n_processes=4,
            sleep=0,
            completion_func=mock_get_completion,
            fake_kwarg=0,  # also test passing a kwarg
        )
        == 0
    )

    # test get_nonmatching_generations
    n_generations = len(corpus.generations)
    metadata_list = [dict(metadata) for metadata in metadata_list]
    popped_metadata = metadata_list.pop(0)
    nonmatching_generations = corpus.get_nonmatching_generations(metadata_list)
    assert len(nonmatching_generations) == 1
    assert nonmatching_generations[0] == popped_metadata
    assert popped_metadata in corpus.generations, "Unexpectedly removed from generations."
    assert n_generations == len(corpus.generations)
    assert len(corpus.get_nonmatching_generations(metadata_list, should_remove_nonmatching=True)) == 1
    assert (
        len(corpus.generations) == n_generations - 1
    ), "Should be one fewer generation after removing non-matching generations."

    # test filter_generations() and overwite()
    n_generations = len(corpus.generations)
    assert corpus.filter_generations() == 0
    assert corpus.filter_generations(lambda _: False) == n_generations
    assert len(corpus.generations) == 0
    corpus.overwrite()


def test_GenerationCorpus_batch_error(tmp_path):
    corpus = generate.GenerationCorpus(tmp_path, "test_corpus")
    assert len(corpus.generations) == 0
    messages = [
        {
            "role": "user",
            "content": "Test query",
        },
    ]
    n_to_generate = 2
    metadata_list = [{"test_id": i, "messages": messages} for i in range(n_to_generate)]
    with pytest.raises(ValueError):
        corpus.batch_generate(
            metadata_list,
            n_processes=1,
            sleep=0,
            completion_func=mock_get_completion_error,
        )
