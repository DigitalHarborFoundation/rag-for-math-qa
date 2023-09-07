import json
import time
from pathlib import Path

import openai


class GenerationCorpus:
    def __init__(self, output_dir: Path, key: str, overwrite: bool = False):
        output_dir.mkdir(exist_ok=True)
        self.output_dir = output_dir
        self.key = key
        self.generation_filepath = output_dir / f"{key}_generations.ndjson"
        self.generations = []
        if not overwrite:
            self.load()

    def load(self):
        if self.generation_filepath.exists():
            with open(self.generation_filepath) as infile:
                for line in infile:
                    d = json.loads(line)
                    self.generations.append(d)

    def _save_generation(self, metadata: dict):
        with open(self.generation_filepath, "a") as outfile:
            outfile.write(json.dumps(metadata) + "\n")

    def is_already_generated(self, messages: list, metadata: dict | None):
        if metadata is None:
            metadata = {}
        for generation in self.generations:
            assert "messages" in generation
            assert "generation" in generation
            if generation["messages"] == messages and generation["generation"] is not None:
                is_metadata_match = True
                for key, value in metadata.items():
                    if key not in generation or generation[key] != value:
                        is_metadata_match = False
                if is_metadata_match:
                    return True
        return False

    def generate(self, messages: list, metadata: dict | None, sleep: float | None = 0.1) -> bool:
        """Generate a new ChatCompletion.

        Args:
            messages (list): List of messages.
            metadata (dict | None): Metadata to save with the completion.
            sleep (float | None, optional): Time to wait after this request, in seconds. Defaults to 0.1.

        Returns:
            bool: True if a new generation was created and saved, False otherwise.
        """
        if metadata is None:
            metadata = {}
        if self.is_already_generated(messages, metadata):
            return False
        generation = get_completion_with_retries(messages)
        metadata["messages"] = messages
        metadata["generation"] = generation
        self.generations.append(metadata)
        self._save_generation(metadata)
        if sleep:
            time.sleep(sleep)  # being a bit polite on repeated api calls
        return True


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
