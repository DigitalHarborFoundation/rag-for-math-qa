import functools
import re

from spacy.lang.en import English


@functools.cache
def get_spacy_english():
    nlp = English()
    return nlp


def get_tokens(string_to_tokenize: str, lower: bool = True, remove_nonalphanumeric_tokens: bool = False) -> list[str]:
    nlp = get_spacy_english()
    doc = nlp.tokenizer(string_to_tokenize)
    if lower:
        tokens = [t.text.lower() for t in doc]
    else:
        tokens = [t.text for t in doc]
    if remove_nonalphanumeric_tokens:
        tokens = [token for token in tokens if re.match("\\w+", token)]
    return tokens
