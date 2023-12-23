# Python image to run discord bot

FROM python:3.11-alpine3.18

# Set working directory

RUN apk add build-base linux-headers

WORKDIR /usr/src/app

# Copy requirements.txt
COPY requirements.txt .
COPY .env .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run bot
CMD ["python", "-u", "main.py"]