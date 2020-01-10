#!/usr/bin/env python3
from elasticsearch import Elasticsearch
from elasticsearch.helpers import reindex

import argparse

from import_to_elasticsearch import maybe_create_index


def copy_es_index(index_source, index_destination):
    es = Elasticsearch()

    # Delete and create target index
    es.indices.delete(index=index_destination, ignore=[404])
    maybe_create_index(index_destination)

    reindex(es, source_index=index_source, target_index=index_destination,
            chunk_size=500)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy 360 ES index")
    parser.add_argument("index_source", type=str, help="Source index name")

    parser.add_argument("index_destination", type=str,
                        help="Destination index name")

    args = parser.parse_args()

    copy_es_index(args.index_source.strip(), args.index_destination.strip())
