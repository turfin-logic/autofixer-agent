FROM python:3.11-slim

WORKDIR /app

# Install git since many bots interact with git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Command to run the bot/agent
CMD ["python", "main.py"]
