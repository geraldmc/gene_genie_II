#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# Class to retrieve, parse and format entries from STRING-DB
#------------------------------------------------------------------------------

# API Documentation: https://www.uniprot.org/help/api
# API Examples: https://www.uniprot.org/help/api_retrieve_entries

import json, re
from urllib.parse import urlencode
from requests import get
from requests.exceptions import RequestException
from contextlib import closing

class StringDB_API(object):
    """USAGE (from app root):
    >> from app.api.stringdb_api import StringDB_API
    >> sdb = StringDB_API('TP53')
    >> resp = sdb.make_request_json()
    >> sdb.parse_json_response(resp)
    """

    def __init__(self, gene_id):    
        self.base = 'https://string-db.org/api/json/get_string_ids'
        self.identifiers = gene_id
        self.species = 9606
        self.url = self.set_url()

    def set_url(self):
        base_url = self.base
        params = dict()
        params['identifiers']=self.identifiers
        params['species']=self.species
        data = urlencode(params)
        url = base_url + '?' + data
        return url

    def make_request_json(self):
        """
        """
        #print (self.url)
        try:
            with closing(get(self.url, stream=True)) as resp: #returns b`json`
                if self.is_jsonish(resp):
                    return json.loads(resp.content.decode("utf-8"))[:3] # first three
                else:
                    return None
        except RequestException as e:
            print('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def is_jsonish(self, resp):
        return True # Taking String-db.org at their word!

    def parse_json_response(self, response):
        """ 
        """
        resp_list = list()
        if len(response) > 1:
            for resp in response:
                resp_list.append(resp)
            return resp_list
        else: return [response] # list with one element

if __name__ == '__main__':
    import argparse
    import random
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--term', help='Search term')
    args = parser.parse_args()
    
    gene_list = ['TP53', 'TNF', 'UBC', 'EGFR', 'VEGFA', 'TGFB1', 'APOE', 
                'IL6', 'TGFB1', 'MTHFR', 'ESR1', 'AKT1', 'NFKB1', 'IL10', 'ACE', 'BRCA1']   
    if (args.term):
        arg = args.term
        sdb = StringDB_API(arg)
        resp = sdb.make_request_json()
        print(sdb.parse_json_response(resp))
    else:
        arg = random.choice(gene_list)
        sdb = StringDB_API(arg)
        resp = sdb.make_request_json()
        print(sdb.parse_json_response(resp))

''' GUTTER ---------------------------------
https://string-db.org/api/json/get_string_ids?identifiers=p53&species=9606
https://string-db.org/api/image/network?identifiers=p53&species=9606
https://string-db.org/api/image/network?identifiers=TP53&add_white_nodes=10&network_flavor=actions

    def set_url(self):
        if self.img: # if True will execute the first condition
            base_url = 'https://string-db.org/api/image/network/get_string_ids'
            params = dict()
            params['identifiers']=self.identifiers
            params['species']=self.species
            data = urlencode(params)
            url = base_url + '?' + data
            return url
        else:
            base_url = self.base
            params = dict()
            params['identifiers']=self.identifiers
            params['species']=self.species
            data = urlencode(params)
            url = base_url + '?' + data
            return url

'''