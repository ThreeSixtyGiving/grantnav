import os


def get_index():
    """ Return the index that is configured can either be the value in an env
    ES_INDEX or a file location to read the index value from"""

    es_index = os.environ.get("ES_INDEX", 'threesixtygiving')
    if os.sep in es_index:
        with open(es_index, 'r') as es_indexfp:
            return str(es_indexfp.read()).strip()
    else:
        return str(es_index)
