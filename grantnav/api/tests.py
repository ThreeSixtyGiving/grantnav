import json
import time
import os

from dataload.import_to_elasticsearch import import_to_elasticsearch
from django.urls import reverse_lazy


prefix = f"{os.path.dirname(__file__)}/../../dataload/test_data/"


def dataload():
    import_to_elasticsearch(
        [
            prefix + 'a002400000KeYdsAAF.json',
            prefix + 'grantnav-20180903134856.json',
            prefix + 'a002400000nO46WAAS.json'
        ],
        clean=True,
        funders=os.path.join(prefix, "funders.jl"),
        recipients=os.path.join(prefix, "recipients.jl")
    )
    #elastic search needs some time to commit its data
    time.sleep(2)


def test_aggregates(client):
    dataload()

    response = client.get(reverse_lazy("api:aggregates"))

    res = json.loads(response.content)

    # For updating test data changes and easier comparison
    # with open("/tmp/new_test_data.json", "w") as f:
    #    f.write(json.dumps(res))

    expected_data = json.load(open(os.path.join(
        os.path.dirname(__file__),
        "test_data",
        "aggregates_expected.json"
        ), "r")
    )

    assert res == expected_data
