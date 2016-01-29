GrantNav - Explore Grants in the 360 data standard
==================================================

[![Build Status](https://travis-ci.org/OpenDataServices/grantnav.svg?branch=master)](https://travis-ci.org/OpenDataServices/grantnav)

We use HuBoard to provide an "agile board" view of our issues https://huboard.com/OpenDataServices/grantnav

Introduction
------------

This is a search tool for data in the 360 giving data format.

This application is currently in a pre-alpha state.

Requirements
------------
This application is built using Django, Elasticsearch and python 3

Installation
------------
Steps to installation:

* Clone the repository
* Change into the cloned repository
* Create a virtual environment (note this application uses python3)
* Activate the virtual environment
* Install dependencies
* Install Elastic search
* Run the development server

.. code:: bash

    git clone https://github.com/OpenDataServices/grantnav.git
    cd grantnav
    virtualenv .ve --python=/usr/bin/python3
    source .ve/bin/activate
    pip install -r requirements_dev.txt
    curl -O https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.1.1/elasticsearch-2.1.1.deb && sudo dpkg -i --force-confnew elasticsearch-2.1.1.deb
    sudo service elasticsearch start
    python manage.py runserver

Note that if you are not on Debian based system you will need to follow https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html#setup-installation to install elasticsearch.
Follow the instructions in your terminal to open the aplication in your browser.

Upload Data
------------

In order to upload some data use the dataload/import_to_elesticsearch.py command line tool e.g:
    python dataload/import_to_elesticsearch.py --clean filename1.csv filename2.csv *.json

The clean command is optional it will delete the index and start again, so leave it off if you want to add just another file to an existing index.
You can specify as many file or patterns as you like at the end of the command.


Run tests
------------

.. code:: bash

    py.test

Make sure elastic search is running.

The tests include functional tests (actually interacting with the website in selenium). These can also be run against a deployed copy of the website:

.. code:: bash

    CUSTOM_SERVER_URL=http://dev.grantnav.opendataservices.coop py.test

The tests delete an elastic search index and repopulate it.  The default index name is threesixtygiving


We also use flake8 to test code quality, see https://github.com/OpenDataServices/developer-docs/blob/master/tests.md#flake8 

