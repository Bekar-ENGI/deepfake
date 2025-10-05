#!/bin/bash
# Script to run FastAPI app with Uvicorn

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
