#!/usr/bin/env bash
# Arrêter le script en cas d'erreur
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate