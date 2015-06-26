#!/usr/bin/env bash
set -e
#set -u
path="."
exclude="lib"
test -z "$1" || path="$1"
pep8 --ignore=E402,E501 "$path" --exclude="$exclude"
exit $?
