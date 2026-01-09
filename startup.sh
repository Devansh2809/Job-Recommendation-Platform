#!/bin/bash
echo "Installing spaCy language model..."
python -m spacy download en_core_web_sm

echo "Starting application..."
gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120