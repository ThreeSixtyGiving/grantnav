import elasticsearch

def get_es():
    ## todo add config options 
    return elasticsearch.Elasticsearch()

