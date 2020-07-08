#!/bin/bash

# prepare
set -e
cd "$(dirname "$0")"

# env path
libpath='pylib'
abspath=$(pwd)/$libpath

# if .venv exists, abort
if test -f ".venv"; then
    echo ".venv already exist. abort."
    exit 0
fi

# make venv
python3 -m venv .venv

# add env path
echo '' >> .venv/bin/activate
echo 'export OLD_PYTHONPATH=$PYTHONPATH' >> .venv/bin/activate
echo "export PYTHONPATH=${abspath}" >> .venv/bin/activate

echo '' >> .venv/bin/postdeactivate
echo 'export PYTHONPATH=$OLD_PYTHONPATH' >> .venv/bin/postdeactivate
echo 'unset OLD_PYTHONPATH' >> .venv/bin/postdeactivate