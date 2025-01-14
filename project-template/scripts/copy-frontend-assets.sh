#!/bin/sh

# Need to call it static here since that's a magic name for Django
mkdir -p main/static/

cp -r main/frontend/img/ main/static/img/
