#!/bin/bash
# Identifier les PID des processus gunicorn sur le port 800-0-2
lsof -i :8000
lsof -i :8001
lsof -i :8002
