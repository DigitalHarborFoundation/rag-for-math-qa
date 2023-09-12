import functools

import datasets
import evaluate

import experiment.tokenize


def compute_macro_f1(passages: list[str], generation: str, discount_text: str | None = None) -> float:
    """Returns the max F1 across all the passages.
    Depending on arguments, this can be Knowledge F1 or just F1.

    SQuAD paper (http://arxiv.org/abs/1606.05250):
    "This metric measures the average overlap between the prediction and ground truth answer.
    We treat the prediction and ground truth as bags of tokens, and compute their F1.
    We take the maximum F1 over all of the ground truth answers for a given question, and then average over all of the questions."

    K-F1++ (https://aclanthology.org/2023.findings-acl.60):
    "Knowledge-F1 (K-F1) ... calculates the unigram overlap between the response and a knowledge snippet K,
    providing a verbatim measure of grounding to the input source.
    We propose K-F1++, a variant of K-F1,
    that captures only the novel information in the generated response and discounts any lexical alignment to the question:
    it calculates the unigram overlap between the response and K,
    after subtracting any tokens appearing in the question from the response."
    To use K-F1++, pass in the text to ignore to discount_text.
    """
    # first create the tokenization function to use
    get_tokens = functools.partial(experiment.tokenize.get_tokens, lower=True, remove_nonalphanumeric_tokens=True)
    generation_tokens = set(get_tokens(generation))
    if discount_text:
        discount_tokens = set(get_tokens(discount_text))
        generation_tokens -= discount_tokens
    n_predicted_tokens = len(generation_tokens)
    if n_predicted_tokens == 0:
        raise ValueError("Expected generation to be non-empty.")
    f1_scores = []
    for passage in passages:
        passage_tokens = set(get_tokens(passage))
        if discount_text:
            passage_tokens -= discount_tokens
        n_ground_truth_tokens = len(passage_tokens)
        if n_ground_truth_tokens == 0:
            continue
        n_correct_tokens = len(passage_tokens & generation_tokens)
        precision = n_correct_tokens / n_predicted_tokens
        recall = n_correct_tokens / n_ground_truth_tokens
        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        f1_scores.append(f1)
    if len(f1_scores) == 0:
        raise ValueError("No non-empty passages.")
    max_f1 = max(f1_scores)
    return max_f1


@functools.cache
def get_bertscore_metric_object() -> evaluate.EvaluationModule:
    """
    See https://huggingface.co/spaces/evaluate-metric/bertscore
    """
    return evaluate.load("bertscore")


@functools.cache
def get_bleurt_metric_object(checkpoint: str = "bleurt-base-512") -> evaluate.EvaluationModule:
    """See https://huggingface.co/spaces/evaluate-metric/bleurt

    Args:
        checkpoint (str, optional): bleurt-base-512, bleurt-large-512, etc. Defaults to "bleurt-base-512".

    Returns:
         evaluate.EvaluationModule: The metric object
    """
    return evaluate.load(
        "bleurt",
        checkpoint=checkpoint,
        module_type="metric",
        download_config=datasets.DownloadConfig(use_etag=False),
    )


def compute_bertscore(passages: list[str], generation: str):
    bert_score = get_bertscore_metric_object()
    references = passages
    predictions = [generation] * len(references)
    score_dict = bert_score.compute(predictions=predictions, references=references, lang="en")
    return max(score_dict["f1"])


def compute_bleurt(passages: list[str], generation: str, compare_to_combined_passage: bool = False):
    bleurt = get_bleurt_metric_object()
    references = passages
    if compare_to_combined_passage:
        references += ["\n".join(passages)]
    predictions = [generation] * len(references)
    scores = bleurt.compute(predictions=predictions, references=references)["scores"]
    return max(scores)
