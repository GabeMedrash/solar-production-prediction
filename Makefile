#######################################
######### Make configuration ##########
#######################################
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

#######################################
############### Venv ##################
#######################################
PYTHON_VERSION = python3.11
VENV_NAME := venv
VENV_BIN := $(VENV_NAME)/bin
PYTHON = $(VENV_BIN)/python3

$(PYTHON):
> $(PYTHON_VERSION) -m venv --copies --upgrade-deps $(VENV_NAME)

venv: $(PYTHON)
> $(PYTHON) -m pip install pip-tools

requirements.txt: venv pyproject.toml
> $(PYTHON) -m piptools compile --generate-hashes --resolver=backtracking -o requirements.txt pyproject.toml

requirements.dev.txt: venv pyproject.toml
> $(PYTHON) -m piptools compile --extra dev --generate-hashes --resolver=backtracking -o requirements.dev.txt pyproject.toml

install-dev: requirements.dev.txt
> $(PYTHON) -m piptools sync requirements.dev.txt
.PHONY: install-dev

install: requirements.txt
> $(PYTHON) -m piptools sync requirements.txt
.PHONY: install

clean:  # Clear proj dir of all .gitignored files
> git clean -Xfd -e "!.env"
.PHONY: clean

#######################################
########### Code quality ##############
#######################################
type-check:
> $(PYTHON) -m mypy --ignore-missing-imports src
.PHONY: type-check

fmt:
> $(PYTHON) -m black src
.PHONY: fmt

import-sort:
> $(PYTHON) -m isort src
.PHONY: import-sort

#######################################
########### Run the thing #############
#######################################
enphase-tokens:
> $(PYTHON) -m src.bin.refresh_enphase_tokens
.PHONY: enphase-tokens

get-actual-energy-production:
> $(PYTHON) -m src.bin.actual_energy_production
.PHONY: get-actual-energy-production

output-plot:
> $(PYTHON) -m src.bin.plot
.PHONY: output-plot

prediction:
> $(PYTHON) -m src.bin.predict
.PHONY: prediction
