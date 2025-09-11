#!/usr/bin/env bash
#
# Set confidential environment variables.

# Set the variable $project_root to be the directory containing this script.
project_root=$( dirname "${BASH_SOURCE[0]}" )
dotenv_bin="$project_root/Python/.venv/bin/dotenv"

# This should be sourced, not executed.
eval $( "$dotenv_bin" -f "$project_root/.env.secret" list --format=export )

unset dotenv_bin
unset project_root