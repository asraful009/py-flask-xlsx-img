#!/bin/bash
virtualenv venv
source "$(pwd)/venv/bin/activate"
pip install -r requirements.txt
python app.py
