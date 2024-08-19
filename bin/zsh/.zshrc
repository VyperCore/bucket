# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

# Jump to BUCKET_ROOT
cd $BUCKET_ROOT

# Custom prompt to make it clear this is the hardware environment
PROMPT="[BKT]:$PROMPT"

# Inherit the user history location
export HISTFILE=$USER_HISTFILE

# Incrementally append to history file
setopt INC_APPEND_HISTORY

# Ensure poetry environment is installed
echo "# Checking Python environment is up-to-date"
if ! poetry env info --path >& /dev/null || ! poetry check --quiet; then
    poetry lock --no-interaction
    poetry install --quiet --no-root --no-interaction
fi

# Activate the poetry shell
echo "# Activating virtual environment"
export VIRTUAL_ENV_DISABLE_PROMPT=1
source $(poetry env info --path)/bin/activate

# Install pre-commit
echo "# Setting up pre-commit hooks"
pre-commit install > /dev/null
