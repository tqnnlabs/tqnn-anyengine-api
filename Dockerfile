FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uvicorn tqnn_api.main:app --host 0.0.0.0 --port ${PORT}"]