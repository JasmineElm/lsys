#!/usr/bin/env bash

### DEBUGGING #################################################################
set -u -e -o errtrace -o pipefail                                               
trap "echo ""errexit: line $LINENO. Exit code: $?"" >&2" ERR                    
IFS=$'\n\t'  

### DESCRIPTION ###############################################################
# Create a virtual environment, activate it, and install the requirements if
# does not exist. If the virtual environment exists, activate it and install
# pass -d to destroy the virtual environment

### VARIABLES #################################################################
venv_name=".venv"
requirements_file="requirements.txt"

_venv_exists() {
    if [ -d "$venv_name" ]; then
        return 0
    else
        return 1
    fi
}

_venv_create() {
    python3 -m venv "$venv_name"
}

_venv_activate() {
    # shellcheck disable=SC1090
    source "$venv_name/bin/activate"
}

_venv_install_requirements() {
    pip install -r "$requirements_file"
}

_destroy_venv() {
    rm -rf "$venv_name"
}

_is_in_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        return 1
    else
        return 0
    fi
}

### MAIN ######################################################################

# no option - create the venv, activate it, and install the requirements
# -d option - destroy the venv

if [ "$1" == "-d" ]; then
    if _venv_exists; then
        _destroy_venv
    else
        echo "No virtual environment to destroy"
    fi
else
    if ! _venv_exists; then
        echo "Creating virtual environment"
        _venv_create
    fi
    _is_in_venv ||\
    echo "Activating virtual environment" &&\
    _venv_activate &&\
    echo "Installing requirements" &&\
    _venv_install_requirements &&\
    echo "Done"
fi
