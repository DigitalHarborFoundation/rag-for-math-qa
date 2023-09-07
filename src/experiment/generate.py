import functools
import json
import multiprocessing as mp
import time
from pathlib import Path
from typing import Callable

from experiment import completion_utils


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

    def _save_generations(self, metadata_list: list[dict]):
        with open(self.generation_filepath, "a") as outfile:
            for metadata in metadata_list:
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
        generation = completion_utils.get_completion_with_retries(messages)
        metadata["messages"] = messages
        metadata["generation"] = generation
        self.generations.append(metadata)
        self._save_generation(metadata)
        if sleep:
            time.sleep(sleep)  # being a bit polite on repeated api calls
        return True

    def batch_generate(
        self,
        metadata_list: list[dict],
        n_processes: int = 4,
        sleep: float = 0.1,
        completion_func: Callable = completion_utils.get_completion_noraise,
    ) -> int:
        """_summary_

        Args:
            metadata_list (list[dict]): List of metadata dictionaries, that must each include a 'messages' key with a list of messages.
            n_processes (int, optional): # processes to spawn in the pool. Defaults to 4.
            sleep (float, optional): Time to sleep between requests IN EACH PROCESS. Defaults to 0.1.
            completion_func (Callable, optional): Function to use to produce generations from a list of messages. Defaults to completion_utils.get_completion_noraise.

        Raises:
            ValueError: If 'messages' is not included in one of the metadata dicts.

        Returns:
            int: Number of new generations. Note this MAY imply generations failed if < len(metadata_list), but only if no metadata were already generated.
        """
        metadata_to_process = []
        for metadata in metadata_list:
            if "messages" not in metadata:
                raise ValueError("Expected 'messages' in all provided metadata.")
            if not self.is_already_generated(metadata["messages"], metadata):
                metadata_to_process.append(metadata)
        if len(metadata_to_process) == 0:
            return 0
        get_completion_func = functools.partial(completion_func, sleep=sleep)
        with mp.Pool(processes=n_processes) as pool:
            message_lists = (md["messages"] for md in metadata_to_process)
            results = pool.map(get_completion_func, message_lists)
            assert len(results) == len(metadata_to_process)
        metadata_completed = []
        for metadata, result in zip(metadata_to_process, results):
            if result is not None:
                metadata["generation"] = result
                metadata_completed.append(metadata)
        if len(metadata_completed) > 0:
            self.generations.extend(metadata_completed)
            self._save_generations(metadata_completed)
        return len(metadata_completed)
