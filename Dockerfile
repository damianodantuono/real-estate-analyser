FROM python:3.11-alpine

# Path: /app
WORKDIR /app

# Path: /requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .

CMD ["python3", "-u" ,"app.py"]
