#!/usr/bin/env python3
import json
import random

#a002400000KeYdsAAF-currency.json  add_new_geo.py	       funders_old.jl				  README.md
#a002400000KeYdsAAF.json		  awefw001p00000zgyHZAAY.json  geo-data-grants-source-tudor-trust-2.json  recipients.jl
#a002400000nO46WAAS.json		  data.json		       geo-data-grants-source-tudor-trust.json	  recipients_old.jl
#a002400000OiDBQAA3.json		  funders.jl		       grantnav-20180903134856.json


source_1 = json.load(open("geo-data-grants-source-tudor-trust.json"))
source_2 = json.load(open("geo-data-grants-source-tudor-trust-2.json"))

geo_arrays = []


for grant in source_1["grants"]:
    geo_arrays.append(grant["additional_data"]["locationLookup"])

for grant in source_2["grants"]:
    geo_arrays.append(grant["additional_data"]["locationLookup"])


for test_data_file in ['a002400000OiDBQAA3.json',
                       'a002400000nO46WAAS.json',
                       'a002400000KeYdsAAF.json',
                       'a002400000KeYdsAAF-currency.json',
                       'awefw001p00000zgyHZAAY.json']:
    test_data = json.load(open(test_data_file))

    for grant in test_data["grants"]:
        try:
            grant["additional_data"]["locationLookup"] = random.choice(geo_arrays)
        except KeyError as e:
            print(e)
            print("continuing")

    json.dump(test_data, open(test_data_file, "w+"))
