import pytest

from experiment import metrics


def test_metric_objects():
    assert metrics.get_bertscore_metric_object() is not None
    assert metrics.get_bleurt_metric_object() is not None


def test_compute_bleurt():
    passages = ["The alphabet is 26 letters long.", "Math is not so easy."]
    generation = "The English alphabet is 26 letters long."
    assert metrics.compute_bleurt(passages, generation) >= 0.3


def test_compute_bertscore():
    passages = ["The alphabet is 26 letters long.", "Math is not so easy."]
    generation = "The English alphabet is 26 letters long."
    assert metrics.compute_bertscore(passages, generation) >= 0.3


def test_compute_macro_f1():
    assert metrics.compute_macro_f1(["Test text", "distractor passage"], "test text") == 1
    assert metrics.compute_macro_f1(["Test"], "test text") == 2 / 3
    assert metrics.compute_macro_f1(["distractor", "distractor passage"], "test text") == 0
    with pytest.raises(ValueError):
        metrics.compute_macro_f1(["test"], "")
    with pytest.raises(ValueError):
        metrics.compute_macro_f1([""], "test")

    # K-F1++
    assert (
        metrics.compute_macro_f1(
            ["George Washington"],
            "Who was the first president? George Washington",
            discount_text="Who was the first president?",
        )
        == 1
    )
