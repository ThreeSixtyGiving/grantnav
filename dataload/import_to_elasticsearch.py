import glob
import json
import requests
import datetime

# curl http://test-360giving.pantheon.io/api/3/action/current_package_list_with_resources | grep -Eo '[^"]+\.json' | sed 's/\\\//\//g' | while read url; do wget "$url"; done

# Delete the index
r = requests.delete('http://localhost:9200/threesixtygiving/')
print(r.text)

# Create it again
r = requests.put('http://localhost:9200/threesixtygiving')
print(r.text)

# Add the extra mapping info we want
# (the rest will be auto inferred from the data we feed in)
r = requests.put('http://localhost:9200/threesixtygiving/_mapping/grant/', data=""" 
{
    "grant": {
        "properties": {
            "filename": {"type": "string", "index": "not_analyzed" },
            "awardDate": {
                "type": "date",
                "ignore_malformed": true
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
                }
              }
            }
        }
    }
}
""")
print(r.text)

#import sys
#sys.exit()

#for f in glob.glob('*.json'):
for fname in ['./Macc-grants.json', './TraffordMBC-Grants.json', './WellcomeTrust-grants.json', './DSDNI.json']: # order by size
    with open(fname) as fp:
        doc = json.load(fp)
        keys = list(doc.keys())
        if len(keys) == 1:
            key = keys[0]
        else:
            raise NotImplementedError

        grants = doc[key]

        for grant in doc[key]:
            grant['filename'] = fname.strip('./')
            r = requests.post('http://localhost:9200/threesixtygiving/grant/', data=json.dumps(grant))
            print(r.text)

