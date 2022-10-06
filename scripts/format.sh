#!/bin/bash
$HOME/.local/bin/poetry run autoflake \
    --remove-all-unused-imports \
    --recursive \
    --remove-unused-variables \
    --in-place \
    buffering_async_logger tests
$HOME/.local/bin/poetry run black buffering_async_logger tests
$HOME/.local/bin/poetry run isort buffering_async_logger tests
