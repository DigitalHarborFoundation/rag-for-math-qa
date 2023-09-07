from experiment import completion_utils

COMPLETION_ERROR_STRING = "completion_utils completion error"


def mock_get_completion_error(*args, **kwargs):
    raise ValueError(COMPLETION_ERROR_STRING)


def mock_get_completion_noerror(*args, **kwargs):
    return "Test completion"


def test_get_completion_noraise(monkeypatch, caplog):
    # verify behavior when errors occur
    monkeypatch.setattr(
        "experiment.completion_utils.get_completion",
        mock_get_completion_error,
    )
    assert completion_utils.get_completion_noraise([], sleep=0, sleep_time_between_attempts=0, max_attempts=2) is None
    for record in caplog.records:
        assert record.name == completion_utils.logger.name
        assert COMPLETION_ERROR_STRING in record.message
    assert (
        len(caplog.records) == 3
    ), "Expected max_attempts error messages from attempts + 1 caught by get_completion_noraise."

    # verify no-error behavior
    monkeypatch.setattr(
        "experiment.completion_utils.get_completion",
        mock_get_completion_noerror,
    )
    assert (
        completion_utils.get_completion_noraise([], sleep=0, sleep_time_between_attempts=0, max_attempts=2)
        == "Test completion"
    )
