# Local Development with Docker Compose

Developers can use Docker Compose to get a local development environment

## Running

```
$ docker-compose -f docker-compose.dev.yml up
```

The website should be available at http://localhost:8000

Use Ctrl-C to exit.

Note you will get an "index_not_found_exception" until you load some data.

## Loading Basic Data

While you do this, the Elasticsearch server must be running - use the general up command.

To load some basic data, assuming your data is saved in `/datastoredata/data/json_all/`:

```
$ docker-compose -f docker-compose.dev.yml run grantnav-web su -c "python dataload/import_to_elasticsearch.py /code/datastoredata/data/json_all/* --clean"
```

## When making changes

If you make changes to either `Dockerfile` or `docker-compose.yml` or any of the `requirements` files you'll need to rebuild:

```
$ docker-compose -f docker-compose.dev.yml down # (if running)
$ docker-compose -f docker-compose.dev.yml build --no-cache
$ docker-compose -f docker-compose.dev.yml up # (to restart)
```

If you edit Python code the changes should be reloaded automatically.


## Compile theme

In order to compile the sass theme run:

``` 
$ docker-compose -f docker-compose.dev.yml run grantnav-web su -c 'pip install -r requirements_dev.txt && pysassc grantnav/frontend/sass/main.scss grantnav/frontend/static/css/theme.css'
```


## Running Tests

To run the tests with docker-compose locally:

```
$ docker-compose -p threesixtygiving-grantnav-test -f docker-compose.test.yml up
```


## Updating Requirements

To update all requirements to the latest version (both production and dev) run:

```
$ docker-compose -f docker-compose.dev.yml run grantnav-web su -c 'pip install -r requirements_dev.txt && pip-compile --upgrade --output-file=requirements.txt requirements.in'
$ docker-compose -f docker-compose.dev.yml run grantnav-web su -c 'pip install -r requirements_dev.txt && pip-compile --upgrade --output-file=requirements_dev.txt requirements_dev.in'
```

You can tweak the pip-compile part of those commands as needed to do other tasks, like only upgrading some packages or adding new packages.

You will then need to rebuild your containers:

```
$ docker-compose -f docker-compose.dev.yml down # (if running)
$ docker-compose -f docker-compose.dev.yml build --no-cache
$ docker-compose -f docker-compose.dev.yml up # (to restart)
```
