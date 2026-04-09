#!/bin/bash
# Run the backend dev server without reloading on data file changes.
# Uvicorn's --reload watches all files by default, including data/*.json,
# which causes constant restarts whenever any request writes to storage.
cd "$(dirname "$0")/app"
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --reload-exclude "data/*"
