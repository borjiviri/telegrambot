#!/usr/bin/env bash
set -e
path="./telegrambot"
test -z "$1" || files="$path"
for file in ${path}/*.py; do
    echo "(pep8) >> $file"
    autopep8 --in-place --aggressive --aggressive "${file}"
done
exit $?
