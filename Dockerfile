FROM python:3.7-slim

# ENV FLASK_APP=app

RUN mkdir /app

COPY app.py /app
COPY requirements.txt /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt 

EXPOSE 5117

CMD ["python", "app.py", "--host", "0.0.0.0","--port", "5117"]
# CMD ["flask", "run", "--host", "0.0.0.0","--port", "5117"]