#!/bin/bash
# Run the crew with cleanenv
cd "$(dirname "$0")"
source cleanenv/bin/activate
cleanenv/bin/python first_project/main.py "$@"
