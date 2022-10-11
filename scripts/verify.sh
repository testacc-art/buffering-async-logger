#!/bin/bash
set -e

$HOME/.local/bin/poetry run black buffering_async_logger tests --check
$HOME/.local/bin/poetry run isort --check-only buffering_async_logger tests
$HOME/.local/bin/poetry run flake8 buffering_async_logger tests
$HOME/.local/bin/poetry run mypy buffering_async_logger tests
$HOME/.local/bin/poetry run bandit -c pyproject.toml -r buffering_async_logger tests

set +e
