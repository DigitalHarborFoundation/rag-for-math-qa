.PHONY: help install ensure-poetry install-precommits test run-streamlit build-docker run-docker remove-docker

export PATH := $(HOME)/.local/bin:$(PATH)

tt:
	@which poetry
	@poetry install

help:
	@echo "Relevant targets are 'install' and 'test'."

install:
	@$(MAKE) ensure-poetry
	@$(MAKE) install-precommits

ensure-poetry:
	@# see issue: https://stackoverflow.com/questions/77019756/make-not-finding-executable-added-to-path-in-makefile
	@if ! command -v poetry &> /dev/null; then \
		echo "Installing poetry"; \
		curl -sSL https://install.python-poetry.org | python - ; \
		echo "Poetry installed, but you might need to update your PATH before make will detect it."; \
	fi
	@poetry install

install-precommits:
	@poetry run pre-commit autoupdate
	@poetry run pre-commit install --overwrite --install-hooks

jupyter:
	@poetry run jupyter lab

test:
	@poetry run pytest --cov=src --cov-report term-missing

build-docker:
	@poetry build
	@docker build -t streamlit -f Dockerfile.streamlit .

run-docker:
	@$(MAKE) remove-docker
	@docker run \
	--name streamlit_container \
	-p 8502:8502 \
	-v ./.streamlit/secrets.toml:/usr/app/.streamlit/secrets.toml \
	streamlit:latest

remove-docker:
	@if docker ps -q --filter "name=streamlit_container" | grep -q .; then \
		echo "Stopping streamlit container"; \
		docker stop streamlit_container; \
	fi
	@if docker ps -a -q --filter "name=streamlit_container" | grep -q .; then \
		echo "Removing streamlit container"; \
		docker remove --volumes streamlit_container; \
	fi

run-streamlit:
	@streamlit run src/streamlit/Annotation_tool.py --
