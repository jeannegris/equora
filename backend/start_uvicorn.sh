#!/bin/bash
set -a
source /var/www/bkautocenter/backend/.env
set +a
#!/home/ubuntu/.local/bin/uvicorn server:app --host 127.0.0.1 --port 8000
PYTHONPATH=/var/www/bkautocenter uvicorn backend.server:app --host 127.0.0.1 --port 8000