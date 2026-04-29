#!/bin/bash

python3 manage.py migrate

cat create_sfu_admin.py | python3 manage.py shell

python3 manage.py runserver 0.0.0.0:8000