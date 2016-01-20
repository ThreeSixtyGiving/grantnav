import glob
import json
import argparse
import requests
import datetime
import uuid
import os
from pprint import pprint
import elasticsearch.helpers

# curl http://test-360giving.pantheon.io/api/3/action/current_package_list_with_resources | grep -Eo '[^"]+\.json' | sed 's/\\\//\//g' | while read url; do wget "$url"; done

def import_to_elasticsearch(files):

    es = elasticsearch.Elasticsearch()

    # Delete the index
    ##r = requests.delete('http://localhost:9200/threesixtygiving/')
    result = es.indices.delete(index='threesixtygiving', ignore=[404])
    pprint(result)



    # Add the extra mapping info we want
    # (the rest will be auto inferred from the data we feed in)
    mappings = {
        "grant": {
            "properties": {
                "_all": {"analyzer": "english", "type": "string"},
                "id": {"type": "string", "index": "not_analyzed" },
                "filename": {"type": "string", "index": "not_analyzed" },
                "awardDate": {
                    "type": "date",
                    "ignore_malformed": True
                },
                "awardDatdateModifiede": {"type": "string", "index": "not_analyzed" },
                "dateModified": {"type": "string", "index": "not_analyzed" },
                "plannedDates": {
                    "properties": {
                        "startDate": {"type": "string", "index": "not_analyzed" },
                        "endDate": {"type": "string", "index": "not_analyzed" }
                    }
                },
                "recipientOrganization" : {
                  "properties" : {
                    "addressLocality" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "charityNumber" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "companyNumber" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "id" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "url" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "name" : {
                      "type" : "string", "copy_to": "recipientOrganization.whole_name"
                    },
                    "whole_name" : {
                      "type" : "string", "index": "not_analyzed"
                    }
                 }
               },
                "fundingOrganization" : {
                  "properties" : {
                    "addressLocality" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "charityNumber" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "companyNumber" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "id" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "url" : {
                      "type" : "string", "index": "not_analyzed"
                    },
                    "name" : {
                      "type" : "string", "copy_to": "fundingOrganization.whole_name"
                    },
                    "whole_name" : {
                      "type" : "string", "index": "not_analyzed"
                    }
                  }
               }
            }
        }
    }

    # Create it again
    result = es.indices.create(index='threesixtygiving', body={"mappings": mappings})
    pprint(result)


    #import sys
    #sys.exit()

    for fname in files:
    #for fname in ['./Macc-grants.json', './TraffordMBC-Grants.json', './WellcomeTrust-grants.json', './DSDNI.json']: # order by size
        with open(fname) as fp:
            doc = json.load(fp)
            keys = list(doc.keys())
            if len(keys) == 1:
                key = keys[0]
            else:
                raise NotImplementedError

            grants = []

            for grant in doc[key]:
                grant['filename'] = fname.strip('./')
                grant['_id'] = str(uuid.uuid4())
                grant['_index'] = 'threesixtygiving'
                grant['_type'] = 'grant'
                grants.append(grant)
            result = elasticsearch.helpers.bulk(es, grants, raise_on_error=False)
            print(fname)
            pprint(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import 360 files in a directory to elasticsearch')
    parser.add_argument('files', help='files to import', nargs='+')
    args = parser.parse_args()
    import_to_elasticsearch(args.files)

