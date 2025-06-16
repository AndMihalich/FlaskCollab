#!/bin/bash
source venv/bin/activate
flask deploy
exec gunicorn -b 0.0.0.0:8000 --access-logfile - --error-logfile - collab:app