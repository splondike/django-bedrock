#!/bin/sh

echo "Press Ctrl-c to detach"
docker attach --detach-keys "ctrl-c" $(docker-compose ps | awk '/backend/{print $1}')
