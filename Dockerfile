FROM python:3.8

RUN apt-get -qq -y update && apt-get -qq -y upgrade
RUN apt-get install -y chromium netcat-traditional

COPY requirements_dev.txt /grantnav/
WORKDIR /grantnav/
RUN pip install -r requirements_dev.txt

EXPOSE 8000

CMD ["/bin/bash"]