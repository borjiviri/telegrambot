#!/usr/bin/env bash
# 28/05/2016 16:24:27
# devnull@libcrack.so

VENV="venv"
V=3
[[ -n "${1}" ]] && V="${1}"
[[ "$BASH_SOURCE" == "${0}" ]] && {
    myself="$(readlink -m ${0#-*})"
    echo "Usage: . ${myself}" > /dev/stderr
    exit 1
} || {
    [[ -d "${VENV}" ]] || {
        echo ">> Creating virtual environment at \"${VENV}\""
        "virtualenv${V}" -p "/usr/bin/python${V}" "${VENV}"
    }
    echo ">> Entering virtual environment \"${VENV}\"" > /dev/stdout
    source "${VENV}/bin/activate"
}
