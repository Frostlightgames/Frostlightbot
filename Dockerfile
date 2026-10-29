FROM python:latest
FROM gorialis/discord.py

WORKDIR /bot

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
