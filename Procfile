web: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keep-alive 5 --access-logfile - --error-logfile -
