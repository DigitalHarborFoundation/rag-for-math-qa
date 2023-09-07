import time

import openai


def get_completion_noraise(messages: list, sleep: float = 0.1) -> str | None:
    """Function wrapper that swallows exceptions, for use with multiprocessing.

    Returns:
        str | None: The completion, or None if an exception was raised.
    """
    try:
        get_completion_with_wait(messages, sleep=sleep)
    except Exception:
        return None


def get_completion_with_wait(messages: list, sleep: float = 0.1) -> str:
    generation = get_completion_with_retries(messages)
    if sleep:
        time.sleep(sleep)  # being a bit polite on repeated api calls
    return generation


def get_completion_with_retries(messages: list, max_attempts: int = 3, sleep_time: float = 5) -> str:
    """Could use a library for this, but let's keep it simple.

    Args:
        messages (list): _description_
        max_attempts (int, optional): Defaults to 3.
        sleep_time (float, optional): Defaults to 5 (seconds).

    Returns:
        str: The completion
    """
    n_attempts = 0
    while n_attempts < max_attempts:
        n_attempts += 1
        try:
            return get_completion(messages)
        except Exception as ex:
            if n_attempts == max_attempts:
                raise ex
            time.sleep(sleep_time * n_attempts)
    raise ValueError(
        f"Exceeded max attempts ({max_attempts}), base sleep interval {sleep_time}s; this error indicates an unexpected logical flow",
    )


def get_completion(messages: list) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        request_timeout=5,
    )
    assistant_message = completion["choices"][0]["message"]["content"]
    return assistant_message
