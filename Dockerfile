FROM python:3.11-slim

# Path: /app
WORKDIR /app
RUN apk --no-cache add musl-dev linux-headers g++
# Path: /requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .

CMD ["python3", "-u" ,"main.py"]
