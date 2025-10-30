#!/bin/bash
flask db upgrade
gunicorn --config gunicorn.conf.py run:app