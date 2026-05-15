#!/bin/bash
python bot/main.py &
uvicorn api:app --host 0.0.0.0 --port $PORT