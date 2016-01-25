import glob
import json
import argparse
import flattentool
import shutil
import uuid
import tempfile
import os
from pprint import pprint
import elasticsearch.helpers

def convert_spreadsheet(file_path, file_type, tmp_dir):
    #file_type = file_name.split('.')[-1]
    encoding = 'utf-8'
    converted_path = os.path.join(tmp_dir, 'output.json')
    if file_type == 'csv':
        destination = os.path.join(tmp_dir, 'grants.csv')
        shutil.copy(file_path, destination)
        try:
            with open(destination, encoding='utf-8') as main_sheet_file:
                main_sheet_file.read()
        except UnicodeDecodeError:
            try:
                with open(destination, encoding='cp1252') as main_sheet_file:
                    main_sheet_file.read()
                encoding = 'cp1252'
            except UnicodeDecodeError:
                encoding = 'latin_1'
        input_name = tmp_dir
    else:
        input_name = file_path
    try:
        flattentool.unflatten(
            input_name,
            output_name=converted_path,
            input_format=file_type,
            main_sheet_name='grants',
            root_id='',
            schema='https://raw.githubusercontent.com/ThreeSixtyGiving/standard/master/schema/360-giving-schema.json',
            convert_titles=True,
            encoding=encoding
        )
    except Exception as err:
        print("Unflattening failed for file {}".format(file_path))
        raise

# curl http://test-360giving.pantheon.io/api/3/action/current_package_list_with_resources | grep -Eo '[^"]+\.json' | sed 's/\\\//\//g' | while read url; do wget "$url"; done

def import_to_elasticsearch(files, clean):

    es = elasticsearch.Elasticsearch()

    # Delete the index
    ##r = requests.delete('http://localhost:9200/threesixtygiving/')
    if clean: 
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

    for file_name in files:
    #for fname in ['./Macc-grants.json', './TraffordMBC-Grants.json', './WellcomeTrust-grants.json', './DSDNI.json']: # order by size
        file_type = file_name.split('.')[-1]
        tmp_dir = ''
        if file_type == 'json':
            json_file_name = file_name
        elif file_type in ('csv', 'xlsx'):
            tmp_dir = tempfile.mkdtemp()
            json_file_name = os.path.join(tmp_dir, 'output.json')
            convert_spreadsheet(file_name, file_type, tmp_dir)
        else:
            print('unimportable file {} (bad) file type'.format(file_name))
            return


        with open(json_file_name) as fp:
            doc = json.load(fp)
            keys = list(doc.keys())
            if len(keys) == 1:
                key = keys[0]
            else:
                raise NotImplementedError

            grants = []

            for grant in doc[key]:
                grant['filename'] = file_name.strip('./')
                grant['_id'] = str(uuid.uuid4())
                grant['_index'] = 'threesixtygiving'
                grant['_type'] = 'grant'
                grants.append(grant)
            result = elasticsearch.helpers.bulk(es, grants, raise_on_error=False)
            print(file_name)
            pprint(result)

        if tmp_dir:
            shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import 360 files in a directory to elasticsearch')
    parser.add_argument('--clean', help='files to import', action='store_true')
    parser.add_argument('files', help='files to import', nargs='+')
    args = parser.parse_args()
    import_to_elasticsearch(args.files, args.clean)

