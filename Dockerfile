FROM python:3.12
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRYTEBYTECODE=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /code/