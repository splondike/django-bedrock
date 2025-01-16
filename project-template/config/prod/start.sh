#!/command/execlineb

with-contenv
s6-setuidgid app
gunicorn --workers 8 --bind 127.0.0.1:8000 --config main/gunicorn_logging.py main.wsgi:application
