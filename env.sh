#!/usr/bin/env bash
#
# Set confidential environment variables.
# This should be sourced, not executed.

# Set the variable $project_root to be the directory containing this script.
project_root=$( dirname "${BASH_SOURCE[0]}" )
dotenv_bin="$project_root/Python/.venv/bin/dotenv"
env_secret="$project_root/.env.secret"

if [[ ! -f "$env_secret" ]]; then
    echo "Error: $env_secret not found." >&2
    exit 1
fi

# Print variable names (not values)
if [[ "${SHOW_SECRET_VARS:-}" == "1" ]]; then
    "$dotenv_bin" -f "$env_secret" list --format=shell | while IFS= read -r line; do
        # Only process non-empty lines that contain '='
        varname="${line%%=*}"
        echo "$varname"
    done
fi

eval $( "$dotenv_bin" -f "$env_secret" list --format=export )

unset dotenv_bin
unset project_root
unset env_secret
