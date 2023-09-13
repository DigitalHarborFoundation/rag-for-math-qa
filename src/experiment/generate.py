import functools
import json
import multiprocessing as mp
import time
from pathlib import Path
from typing import Callable

from experiment import completion_utils


def is_valid_generation(generation: dict):
    return "messages" in generation and "generation" in generation


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

    def overwrite(self):
        self._save_generations(self.generations, write_mode="w")

    def filter_generations(
        self,
        should_include_func: Callable = is_valid_generation,
        should_remove_func: Callable | None = None,
    ) -> int:
        filtered_generations = []
        for generation in self.generations:
            if should_include_func(generation) and (should_remove_func is None or not should_remove_func(generation)):
                filtered_generations.append(generation)
        n_removed = len(self.generations) - len(filtered_generations)
        self.generations = filtered_generations
        return n_removed

    def _save_generation(self, metadata: dict):
        with open(self.generation_filepath, "a") as outfile:
            outfile.write(json.dumps(metadata) + "\n")

    def _save_generations(self, metadata_list: list[dict], write_mode: str = "a"):
        with open(self.generation_filepath, write_mode) as outfile:
            for metadata in metadata_list:
                outfile.write(json.dumps(metadata) + "\n")

    def is_already_generated(
        self,
        messages: list,
        metadata: dict | None,
        exclude_keys: set[str] = {"generation", "messages"},
    ) -> bool:
        """Determine if a generation was already created for this set of messages (and corresponding metadata).

        Args:
            messages (list): Message list to pass to the OpenAI API.
            metadata (dict | None): Optional metadata associated with the generation.
            exclude_keys (set[str], optional): Metadata keys to ignore when determining if this is a duplicate. Defaults to {"generation", "messages"}.

        Returns:
            bool: True if already in self.generations, False otherwise.
        """
        if metadata is None:
            metadata = {}
        for generation in self.generations:
            assert "messages" in generation
            assert "generation" in generation
            if generation["messages"] == messages and generation["generation"] is not None:
                is_metadata_match = True
                for key, value in metadata.items():
                    if key in exclude_keys:
                        continue
                    if key not in generation or generation[key] != value:
                        is_metadata_match = False
                if is_metadata_match:
                    return True
        return False

    def generate(
        self,
        messages: list,
        metadata: dict | None,
        sleep: float | None = 0.1,
    ) -> bool:
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

    def batch_filter_not_already_generated(self, metadata_list: list[dict]) -> list[dict]:
        metadata_to_process = []
        for metadata in metadata_list:
            if "messages" not in metadata:
                raise ValueError("Expected 'messages' in all provided metadata.")
            if not self.is_already_generated(metadata["messages"], metadata):
                metadata_to_process.append(metadata)
        return metadata_to_process

    def get_nonmatching_generations(
        self,
        metadata_list: list[dict],
        exclude_keys: set[str] = {"generation", "messages"},
        should_remove_nonmatching: bool = False,
    ) -> list[dict]:
        nonmatching_generations = []
        nonmatching_inds = []
        for i, generation in enumerate(self.generations):
            generation_match_found = False
            for metadata in metadata_list:
                is_metadata_match = True
                for key, value in metadata.items():
                    if key in exclude_keys:
                        continue
                    if key not in generation or generation[key] != value:
                        is_metadata_match = False
                        break
                if is_metadata_match:
                    generation_match_found = True
                    break
            if not generation_match_found:
                nonmatching_generations.append(generation)
                nonmatching_inds.append(i)
        if should_remove_nonmatching:
            for ind in sorted(nonmatching_inds, reverse=True):
                self.generations.pop(ind)
        return nonmatching_generations

    def batch_generate(
        self,
        metadata_list: list[dict],
        n_processes: int = 4,
        sleep: float = 0.1,
        completion_func: Callable = completion_utils.get_completion_noraise,
        **kwargs,
    ) -> int:
        """_summary_

        Args:
            metadata_list (list[dict]): List of metadata dictionaries, that must each include a 'messages' key with a list of messages.
            n_processes (int, optional): # processes to spawn in the pool. Defaults to 4.
            sleep (float, optional): Time to sleep between requests IN EACH PROCESS. Defaults to 0.1.
            completion_func (Callable, optional): Function to use to produce generations from a list of messages. Defaults to completion_utils.get_completion_noraise.
            Other keyword args are passed to completion_func

        Raises:
            ValueError: If 'messages' is not included in one of the metadata dicts.

        Returns:
            int: Number of new generations. Note this MAY imply generations failed if < len(metadata_list), but only if no metadata were already generated.
        """
        metadata_to_process = self.batch_filter_not_already_generated(metadata_list)
        if len(metadata_to_process) == 0:
            return 0
        get_completion_func = functools.partial(completion_func, sleep=sleep, **kwargs)
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
