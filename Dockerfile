FROM python:3.14-slim

WORKDIR /bot

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
