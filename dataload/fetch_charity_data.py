from html.parser import HTMLParser
import requests
from io import StringIO
import zipfile
import os
import csv
import titlecase
import json

current_dir = os.path.dirname(os.path.realpath(__file__))

latest_zip_file = os.path.join(current_dir, 'charity_registory.zip')
charity_names_json = os.path.join(current_dir, 'charity_names.json')


def title_exceptions(word, **kwargs):
    if word.lower() in ['a', 'an', 'of', 'the', 'is', 'or']:
        return word.lower()
    if word.upper() in ['UK', 'FM', 'YMCA']:
        return word.upper()


class getFirstExtractFile(HTMLParser):
    def __init__(self, *args, **kw):
        self.first_url = None
        super().__init__(*args, **kw)

    def handle_starttag(self, tag, attrs):
        if self.first_url:
            return
        href = dict(attrs).get('href')
        if href:
            if 'RegPlusExtract' in href:
                self.first_url = href


def download_latest_file():
    parser = getFirstExtractFile()
    parser.feed(requests.get('http://data.charitycommission.gov.uk/default.aspx').text)
    response = requests.get(parser.first_url)

    with open(latest_zip_file, 'wb+') as fd:
        for chunk in response.iter_content(10000):
            fd.write(chunk)


# Partially copied from https://github.com/ncvo/charity-commission-extract/blob/master/bcp.py
def convert(bcpdata, lineterminator=b'*@@*', delimiter=b'@**@', quote=b'"', newdelimiter=b',', col_headers=None, escapechar=b'\\', newline=b'\n'):
    bcpdata = bcpdata.replace(escapechar, escapechar + escapechar)
    bcpdata = bcpdata.replace(quote, escapechar + quote)
    bcpdata = bcpdata.replace(delimiter, quote + newdelimiter + quote)
    bcpdata = bcpdata.replace(lineterminator, quote + newline + quote)
    return b'"' + bcpdata + b'"'


def get_json():
    zipped_data = zipfile.ZipFile(latest_zip_file, 'r')
    csv_text = convert(zipped_data.open('extract_charity.bcp').read()).decode('latin_1')
    csv_text = csv_text.replace('\0', '')

    name_mapping = {}
    for line in csv.reader(StringIO(csv_text)):
        try:
            if line[1] == '0':
                name_mapping['GB-CHC-' + line[0]] = titlecase.titlecase(line[2].strip(), title_exceptions)
        except:
            print(line, ' not converted')

    with open(charity_names_json, 'w+') as json_file:
        json.dump(name_mapping, json_file)

if __name__ == '__main__':
    download_latest_file()
    get_json()
    os.remove(latest_zip_file)
