import html
import json
import logging
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

OVERFLOW_RESPONSE = "No more responses to annotate"
OVERFLOW_DOCUMENT = "n/a"
OVERFLOW_QUERY = "No more student queries in this survey, just click through to the end."

survey_id_key = "RoriSurveyId"
response_keys = ["Response1Q", "Response2Q", "Response3Q"]
query_text_key = "QueryTextQ"
document_key = "DocumentQ"


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def get_template(template_filepath: Path):
    with open(template_filepath) as infile:
        survey_text = infile.read()
    validate_template_survey_text(survey_text)
    return survey_text


def validate_template_survey_text(survey_text, expected_survey_size: int = 15):
    assert json.loads(survey_text)

    # validate expected keys
    for key in response_keys + [query_text_key, document_key]:
        for i in range(1, expected_survey_size + 1):
            qkey = key + str(i)
            assert qkey in survey_text, qkey


def convert_text(text, use_br=True):
    # not sure this replace is necessary, but I was having some issues with escaping
    text = text.replace("\\", "/")
    text = html.escape(text)
    if use_br:
        text = "<p>" + "</p><br><p>".join(text.split("\n")) + "</p>"
    else:
        text = "<p>" + "</p><p>".join(text.split("\n")) + "</p>"
    return text


def create_surveys(
    df: pd.DataFrame,
    template_survey_text: str,
    survey_dir: Path,
    survey_size: int = 15,
    rng: np.random.Generator = None,
) -> pd.DataFrame:
    """Assumed columns:
    - generation
    - query
    - document
    """
    if rng is None:
        rng = np.random.default_rng()
    rows = []
    for query, group in df.groupby("query"):
        assert len(group) == 3, "Qualtrics survey hard-coded to accept 3 responses."
        assert group["generation"].nunique() == 3, "Generations/responses should be unique."
        for key in ["document"]:
            n_unique = group[key].nunique()
            if n_unique != 1:
                logging.warning(f"Expected 1 unique value in column {key}, found {n_unique}")
        # shuffle rows
        group = group.sample(frac=1, random_state=rng)
        # build new data structure
        responses = []
        metas = []
        for i in range(3):
            row = group.iloc[i]
            response = row.generation
            responses.append(response)
            meta = row.to_dict()
            del meta["document"]
            del meta["generation"]
            del meta["query"]
            metas.append(meta)
        row = [query, group.iloc[0]["document"], *responses, *metas]
        rows.append(row)
    # randomize row order
    rng.shuffle(rows)

    survey_dir.mkdir(exist_ok=True)
    for i, survey_rows in enumerate(chunker(rows, survey_size)):
        survey_id = f"s_{datetime.now().strftime('%Y%m%d')}_{i+1}/{math.ceil(len(rows) / survey_size)}"
        survey_text = create_survey(survey_id, survey_rows, template_survey_text, survey_size)
        survey_filepath = survey_dir / f"Rori_ranking_annotations_-_survey{i}.qsf"
        with open(survey_filepath, "w") as outfile:
            outfile.write(survey_text)
        for row in survey_rows:
            row.append(survey_id)

    # build survey_df from rows
    survey_df = pd.DataFrame(
        rows,
        columns=[
            "query",
            "document",
            "response1",
            "response2",
            "response3",
            "response1_meta",
            "response2_meta",
            "response3_meta",
            "survey_id",
        ],
    )
    return survey_df


def create_survey(survey_id: str, rows: list, template_survey_text: str, survey_size: int = 15) -> str:
    survey_text = template_survey_text
    survey_text = survey_text.replace(survey_id_key, survey_id)
    for i in range(1, survey_size + 1):
        if i - 1 < len(rows):
            row = rows[i - 1]
            query, document, r1, r2, r3, _, _, _ = row
        else:
            query = OVERFLOW_QUERY
            document = OVERFLOW_DOCUMENT
            r1, r2, r3 = OVERFLOW_RESPONSE, OVERFLOW_RESPONSE, OVERFLOW_RESPONSE
        responses = [r1, r2, r3]
        for key, response in zip(response_keys, responses):
            qkey = key + str(i)
            text = convert_text(response, use_br=False)
            survey_text = survey_text.replace(qkey, text, 1)
        survey_text = survey_text.replace(query_text_key + str(i), convert_text(query), 1)
        survey_text = survey_text.replace(document_key + str(i), convert_text(document), 1)
    # verify that we've created valid JSON
    survey_text = json.dumps(json.loads(survey_text))
    return survey_text
