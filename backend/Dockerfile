# Dockerfile
FROM python:3.10-slim

# system deps
RUN apt-get update && apt-get install -y ffmpeg build-essential libsndfile1 git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy
COPY ./app /app/app
COPY requirements.txt /app/requirements.txt

# install python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
