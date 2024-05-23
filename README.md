# Retrieval-augmented generation to improve math question-answering: trade-offs between groundedness and human preference

[![arXiv](https://img.shields.io/badge/arXiv-2310.03184-b31b1b.svg)](https://arxiv.org/abs/2310.03184)
[![License](https://img.shields.io/github/license/DigitalHarborFoundation/rag-for-math-qa)](https://github.com/DigitalHarborFoundation/rag-for-math-qa/blob/main/LICENSE)


This repository contains analysis code, prompts, surveys, figures, and data for the paper "Retrieval-augmented generation to improve math question-answering: trade-offs between groundedness and human preference".

This repository forks the [`llm-math-education`](https://github.com/DigitalHarborFoundation/llm-math-education) package.

Cite [the paper](https://arxiv.org/abs/2310.03184) using the CITATION.cff file and dropdown:

>Zachary Levonian, Chenglu Li, Wangda Zhu, Anoushka Gade, Owen Henkel, Millie-Ellen Postle, and Wanli Xing. 2023. Retrieval-augmented Generation to Improve Math Question-Answering: Trade-offs Between Groundedness and Human Preference. In _NeurIPS’23 Workshop on Generative AI for Education (GAIED)_, New Orleans, USA. DOI:https://doi.org/10.48550/arXiv.2310.03184

## Development

Primary code contributor:

 - Zachary Levonian (<zach@levi.digitalharbor.org>)

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

 ## Other notes

 ### Poster figures

Some logos are present in the posters directory.

The Digital Harbor Foundation logo was created using [`rsvg-convert`](https://man.archlinux.org/man/rsvg-convert.1.en), installed via `brew`.

I manually adjusted the source svg (dhf-logo-vector-blue.svg) to use DHF blue (#0091c9) rather than black (#010101).

```bash
brew install librsvg
rsvg-convert -d 150 -p 150 -h 2in figures/dhf-logo-vector-blue.svg > figures/dhf-poster-logo.png
```

Converting the system diagram (converted from draw.io as an SVG, with embedded fonts):

```bash
rsvg-convert -d 150 -p 150 -h 4in figures/system-diagram.svg > figures/system-diagram-poster.png
```
