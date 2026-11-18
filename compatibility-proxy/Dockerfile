FROM python:3.12-slim

WORKDIR /app

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output appears immediately in Docker logs
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .

EXPOSE 8000

CMD ["uvicorn", "proxy:app", "--host", "0.0.0.0", "--port", "8000"]