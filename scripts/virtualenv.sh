#!/usr/bin/env bash
[[ -d venv ]] || {
    virtualenv -p /usr/bin/python3.4 venv
}
source venv/bin/activate
