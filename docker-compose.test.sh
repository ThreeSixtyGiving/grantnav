#!/bin/bash

set -e

if [ ! -f "/bin/netcat" ]; then
  apt-get update
  apt-get install -y chromium netcat
fi

pip install -r requirements_dev.txt

if [ ! -f "/wait_for" ]; then
  wget -O /wait_for https://raw.githubusercontent.com/eficode/wait-for/v2.1.2/wait-for
  chmod a+x  /wait_for
fi

/wait_for elasticsearch-test:9200
/wait_for elasticsearch-test:9300

py.test

