import pytest

from experiment import metrics


def test_compute_bertscore():
    metrics.compute_bertscore()


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
