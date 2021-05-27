FROM python:3.6.13-buster

RUN mkdir /code
COPY . /code/
WORKDIR /code/
RUN pip install -r /code/requirements.txt

# This CMD never actually used; currently Docker Compose replaces it.
# Should be command for production web server later.
CMD sh -c ' ls'

EXPOSE 8000
