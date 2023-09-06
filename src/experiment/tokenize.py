import functools

from spacy.lang.en import English


@functools.cache
def get_spacy_english():
    nlp = English()
    return nlp


def get_tokens(string_to_tokenize: str, lower: bool = True) -> list[str]:
    nlp = get_spacy_english()
    doc = nlp.tokenizer(string_to_tokenize)
    if lower:
        tokens = [t.text.lower() for t in doc]
    else:
        tokens = [t.text for t in doc]
    return tokens
