# SPDX-FileCopyrightText: Enno Hermann
#
# SPDX-License-Identifier: CC0-1.0

.PHONY: test style lint

test:
	uv run --all-extras coverage run

style:
	uv run ruff format

lint:
	uv run pre-commit run --all-files
