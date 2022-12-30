# See https://tech.davis-hansson.com/p/make/
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = >

##########################
######### Setup ##########
##########################

PYTHON_VERSION = python3.11
VENV_NAME := venv
VENV_BIN := $(VENV_NAME)/bin
ACTIVATE = $(VENV_BIN)/activate
PYTHON = $(VENV_BIN)/python3

$(PYTHON):
> $(PYTHON_VERSION) -m venv --copies --upgrade-deps $(VENV_NAME)

venv: $(PYTHON)
> $(PYTHON) -m pip install pip-tools

requirements.txt: venv pyproject.toml
> $(PYTHON) -m piptools compile --generate-hashes --resolver=backtracking -o requirements.txt pyproject.toml

requirements.dev.text: venv pyproject.toml
> $(PYTHON) -m piptools compile --extra dev --generate-hashes --resolver=backtracking -o requirements.dev.text pyproject.toml

install: requirements.txt requirements.dev.text
> $(PYTHON) -m piptools sync requirements.dev.text requirements.txt

##########################
###### Code quality ######
##########################
type-check:
> $(PYTHON) -m mypy --ignore-missing-imports src
.PHONY: type-check

fmt:
> $(PYTHON) -m black src
.PHONY: fmt

import-sort:
> $(PYTHON) -m isort src
.PHONY: import-sort