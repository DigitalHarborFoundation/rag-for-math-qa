# Retrieval-augmented generation to improve math question-answering: trade-offs between groundedness and human preference

This repository contains analysis code, prompts, surveys, figures, and data for the paper "Retrieval-augmented generation to improve math question-answering: trade-offs between groundedness and human preference".

This repository forks the [`llm-math-education`](https://github.com/DigitalHarborFoundation/llm-math-education) package.

Cite [the paper](https://arxiv.org/abs/2310.03184) using the CITATION.cff file and dropdown:

>Zachary Levonian, Chenglu Li, Wangda Zhu, Anoushka Gade, Owen Henkel, Millie-Ellen Postle, and Wanli Xing. 2023. Retrieval-augmented Generation to Improve Math Question-Answering: Trade-offs Between Groundedness and Human Preference. In _NeurIPS’23 Workshop on Generative AI for Education (GAIED)_, New Orleans, USA. DOI:https://doi.org/10.48550/arXiv.2310.03184

## Development

Primary code contributor:

 - Zachary Levonian (<zach@digitalharbor.org>)

## Local development setup

This project uses `make` and `Poetry` to manage and install dependencies.

On Windows, you'll need to use WSL and maybe make some other changes.

### Python development

Use `make install` to install all needed dependencies (including the pre-commit hooks and Poetry).

You'll probably need to manually add Poetry to your PATH, e.g. by updating your `.bashrc` (or relevant equivalent):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Run tests

```bash
make test
```

### Run Jupyter Lab

```bash
make jupyter
```

Which really just runs `poetry run jupyter lab`, so feel free to customize your Jupyter experience.

### Other useful commands

 - `poetry run <command>` - Run the given command, e.g. `poetry run pytest` invokes the tests.
 - `poetry add <package>` - Add the given package as a dependency. Use flag `-G dev` to add it as a development dependency.
