import pathlib
from datetime import datetime

import pandas as pd
import pytest

from experiment import qualtrics


@pytest.fixture(scope="module")
def qualtrics_template_filepath(pytestconfig) -> pathlib.Path:
    template_filepath = pytestconfig.rootpath / "data" / "raw" / "qualtrics" / "Rori_ranking_annotations_-_template.qsf"
    if not template_filepath.exists():
        pytest.skip(f"Qualtrics template at {template_filepath} does not exist.")
    return template_filepath


def test_create_surveys(qualtrics_template_filepath, tmp_path):
    template_survey_text = qualtrics.get_template(qualtrics_template_filepath)
    assert template_survey_text is not None

    survey = qualtrics.create_survey("survey_id0", [], template_survey_text)
    assert qualtrics.OVERFLOW_RESPONSE in survey

    survey_dir = tmp_path / "test_surveys"
    df = pd.DataFrame(
        [
            ["q1", "d1", "none", "g1", "a"],
            ["q1", "d1", "low", "g2", "a"],
            ["q1", "d1", "high", "g3", "a"],
        ],
        columns=["query", "document", "guidance", "generation", "metadata"],
    )
    survey_df = qualtrics.create_surveys(df, template_survey_text, survey_dir)
    row = survey_df.iloc[0]
    assert row["query"] == "q1"
    assert row["document"] == "d1"
    assert set(row[["response1", "response2", "response3"]]) == {"g1", "g2", "g3"}
    assert row["survey_id"] == f"s_{datetime.now().strftime('%Y%m%d')}_1/1"
