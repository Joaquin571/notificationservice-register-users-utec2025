$env:PYTHONUNBUFFERED="1"
uvicorn app.main:app --reload --port 8081
