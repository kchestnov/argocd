#!/bin/bash

# Usage: source this script
# Example: source env.sh

venvdir="${VENVDIR:-"$HOME/.venvs/$(basename $(pwd))"}"

mkdir -p "$venvdir"

if [ ! -f "${venvdir}/bin/activate" ]
then
  python3 -m venv "$venvdir"
fi

source "${venvdir}/bin/activate"

python -m pip install pip==22.0.2

if [ -f requirements.txt ]
then
  python -m pip install -r requirements.txt
fi

echo "PyEnv for the $(basename $(pwd)) project has been configured"
