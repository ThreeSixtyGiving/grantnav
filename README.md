GrantNav - Explore Grants in the 360 data standard
==================================================

[![Build Status](https://travis-ci.org/OpenDataServices/grantnav.svg?branch=master)](https://travis-ci.org/OpenDataServices/grantnav)

We use HuBoard to provide a Kanban board visualisation of our workflow and issues https://huboard.com/OpenDataServices/grantnav

Introduction
------------

This is a search tool for data in the 360 giving data format.

This application is currently undergoing final testing before a production launch.

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
* Install Java 7+ (this is a requirement for Elasticsearch but the packages don't depend on any Java package)
* Install Elastic search
* Run the development server

On a Debian-based Linux distribution, your commands will probably look like this:
```
git clone https://github.com/OpenDataServices/grantnav.git
cd grantnav
virtualenv .ve --python=/usr/bin/python3
source .ve/bin/activate
pip install -r requirements_dev.txt
sudo apt-get install openjdk-7-jre
curl -O https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.1.1/elasticsearch-2.1.1.deb && sudo dpkg -i --force-confnew elasticsearch-2.1.1.deb
sudo service elasticsearch start
python manage.py runserver
```

Note that if you are not on Debian based system you will need to follow https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html#setup-installation to install elasticsearch.
Follow the instructions in your terminal to open the aplication in your browser.


Upload Data
------------

In order to upload some data use the dataload/import_to_elasticsearch.py command line tool e.g:
    python dataload/import_to_elasticsearch.py --clean filename1.csv filename2.csv *.json

The clean command is optional; it will delete the index and start again, so leave it off if you want to add just another file to an existing index.
You can specify as many file or patterns as you like at the end of the command.

### Getting data for upload

There is a list of 360Giving datasets at http://www.threesixtygiving.org/data/find-data/. There's an API for this list http://data.threesixtygiving.org/data.json and some code to help download from it -  https://github.com/ThreeSixtyGiving/datagetter

If your data is in a flat format (eg Excel spreadsheet, CSV), or needs validating, you can use [CoVE](http://cove.opendataservices.coop/360/) to convert and validate your data.

### Provenance JSON

Most parts of GrantNav work fine without provenance information. However, in order for the publisher/datasets pages to work correctly you must point the `PROVENANCE_JSON` environment variable at a local copy of [data.json](http://data.threesixtygiving.org/data.json). You must also load the data into GrantNav using filenames that correspond to the identifiers in this JSON. The [datagetter](https://github.com/ThreeSixtyGiving/datagetter) saves files with the correct name, and also makes a copy of data.json for you.

e.g.

```
cd datagetter/data/json_acceptable_license_valid
python path/to/grantnav/dataload/import_to_elasticsearch.py --clean *
cd path/to/grantnav
PROVENANCE_JSON=path/to/datagetter/data/data_acceptable_license_valid.json python manage.py runserver
```


Compile theme
-------------

In order to compile the sass theme run:

```
sassc grantnav/frontend/sass/main.scss grantnav/frontend/static/css/theme.css
```


Run tests
------------

```
py.test
```

Make sure elastic search is running.

The tests include functional tests (actually interacting with the website in selenium). These can also be run against a deployed copy of the website:

```
CUSTOM_SERVER_URL=http://dev.grantnav.opendataservices.coop py.test
```

The tests delete an elastic search index and repopulate it.  The default index name is threesixtygiving

We also use flake8 to test code quality, see https://github.com/OpenDataServices/developer-docs/blob/master/tests.md#flake8 


Adding and updating requirements
--------------------------------

Add a new requirements to ``requirements.in`` or ``requirements_dev.in`` depending on whether it is just a development requirement or not.

Then, run ``./update_requirements --new-only`` this will populate ``requirements.txt`` and/or ``requirements_dev.txt`` with pinned versions of the new requirement and it's dependencies.

WARNING: The ``./update_requirements`` script will delete and recreate your current ``.ve`` directory.

``./update_requirements`` without any flags will update all pinned requirements to the latest version. Generally we don't want to do this at the same time as adding a new dependency, to make testing any problems easier.



Fetching external datasets
--------------------------------

### Open code point

Go to https://www.ordnancesurvey.co.uk/opendatadownload/products.html and request a download of Code-Point open. The will send you a link to a zip file and extract that zip into a directory and cd into that directory.  It should contain a Docs and a Data directory. 

Get the second line of the heading file with the following command:

```
cat Doc/Code-Point_Open_Column_Headers.csv | head -2 | tail -1 > HEADING.csv
```
Get all the data and the heading in one file and gz the file.

```
cat HEADING.csv Data/CSV/* | gzip > codepoint_with_heading.csv.gz
```

Get csv2xlsx and convert sheets to single csv
```
pip install csv2xlsx
echo 'name,code' > codelist.csv
xlsx2csv Doc/Codelist.xlsx -a -p '' -E Metadata AREA_CODES >> codelist.csv
```

Finally you need the NHS codelist which is an xls file and for this you need libreoffice and make sure libreoffice is not open on your system.
```
libreoffice --headless --convert-to csv Doc/NHS_Codelist.xls
awk -F, '{print $2,$1}' OFS=, NHS_Codelist.csv >> codelist.csv
```

Then copy codepoint_with_heading.csv.gz and codelist.csv to the dataload directory.

### Charity commission data.

This is a single script but takes a long time.

```
python dataload/fetch_charity_data.py
```


