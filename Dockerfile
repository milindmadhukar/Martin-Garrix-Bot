# Python image to run discord bot

FROM python:3.11-slim-buster

# Set working directory

APK add --no-cache gcc musl-dev linux-headers

WORKDIR /usr/src/app

# Copy requirements.txt
COPY requirements.txt .
COPY .env .

# Install dependencies
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Run bot
CMD ["python", "main.py"]
