#!/bin/sh
venv/bin/coverage run --branch --include="*feincms3/*" --omit="*tests*" ./manage.py test -v 2 testapp
venv/bin/coverage html
