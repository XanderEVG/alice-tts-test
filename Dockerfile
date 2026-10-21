FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alice_tts.py .

EXPOSE 5000

CMD ["python", "alice_tts.py"]