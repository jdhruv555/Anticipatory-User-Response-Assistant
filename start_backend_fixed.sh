#!/bin/bash
cd backend
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH
uvicorn main:app --reload --host 0.0.0.0 --port 8000
