FROM ubuntu:latest

# Install python3
RUN apt-get update
RUN apt-get install -y python3.5 python3-pip

# Copy requirements.txt
COPY requirements.txt /opt/example/requirements.txt

# Install dependencies
RUN pip3 install -r /opt/example/requirements.txt

# Copy app directory
COPY . /opt/example

# Set default directory
ENV HOME /opt/example
WORKDIR /opt/example

# Set environ vars
ENV REDIS_HOST 'exampleredis'
ENV REDIS_PORT 6379

# Expost port
EXPOSE 8080

# Command to run on start
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "example.wsgi"]
