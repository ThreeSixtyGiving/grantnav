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

To load some basic data:

```
$ docker-compose -f docker-compose.dev.yml run grantnav-web su -c 'wget -O  scvo-test-data.json https://scvo.scot/support/coronavirus/funding/scottish-government/community-recovery/crf/recipients/data.json && python dataload/import_to_elasticsearch.py --clean scvo-test-data.json'
```

## When making changes

If you make changes to either `Dockerfile` or `docker-compose.yml` or any of the `requirements` files you'll need to rebuild:

```
$ docker-compose -f docker-compose.dev.yml down # (if running)
$ docker-compose -f docker-compose.dev.yml build --no-cache
$ docker-compose -f docker-compose.dev.yml up # (to restart)
```

If you edit Python code the changes should be reloaded automatically.

