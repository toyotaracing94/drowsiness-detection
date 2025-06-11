#!/bin/bash
source venv/bin/activate
exec uvicorn main:app --host 0.0.0.0