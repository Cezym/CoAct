FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app.py /app/main.py

# Default port in tiangolo image is 80; we expose 8001 for clarity when running locally.
ENV PORT=80
