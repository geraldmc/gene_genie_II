#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------
# Class to retrieve, parse and format json from Entrez
#------------------------------------------------------------------

# API Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25501/
# API Examples: https://www.ncbi.nlm.nih.gov/books/NBK25498/

import json
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen, Request
import xmltodict
from urllib.parse import urlencode
import pandas as pd
import numpy as np

from Bio import Entrez
import xml.etree.ElementTree as ET

class EntrezAPI(object):
    """USAGE (from app root):
    >> from app.api.entrez_api import EntrezAPI
    >> gene_id_list = EntrezAPI().search_gene('BRCA1')
    >> print(gene_id_list['IdList'])
    >> pmid_id_list = EntrezAPI().search_pubmed('BRCA1')
    >> print(pmid_id_list['IdList'])
    """
    
    def __init__(self, DEBUG=False, RETMAX=5):
        self.email = 'gmccoll2@jhu.edu'
        self.api_key = 'c9ac67b1726a7f6b37f74564c823c18ddb08'
        self.RETMAX = RETMAX # number of records returned
        self.DEBUG = DEBUG
        self.with_species_orthologs = True # related results
    
    def search_gene(self, gene):
        Entrez.email = self.email
        handle = Entrez.esearch(db='gene', sort='relevance', 
                                retmax=self.RETMAX,
                                retmode='xml',
                                api_key=self.api_key, 
                                term=gene)
        results = Entrez.read(handle)
        return results

    def search_pubmed(self, query):
        Entrez.email = self.email
        handle = Entrez.esearch(db='pubmed', sort='relevance', 
                                retmax=self.RETMAX,
                                retmode='xml', 
                                api_key=self.api_key,
                                term=query)
        results = Entrez.read(handle)
        return results

    def get_pubmed_from_gene_id(self, gene_id):
        """bioDBnet - biological DataBase network
        """
        url = 'https://biodbnet-abcc.ncifcrf.gov/webServices/rest.php/biodbnetRestApi.xml?' \
            'method=db2db&format=row&input=geneid&outputs=pubmedid&inputValues={d}'.format(d=gene_id)
        try:
            response = urlopen(url)
        except URLError:
            xml_dict = ''
            print('Connection failed.')
        else:
            xml = response.read().decode()
            xml_dict = xmltodict.parse(xml)
        pmids = xml_dict['response']['item']['PubMedID'].split('//')[0:3] # take 3
        return pmids

    def get_uniprot_from_entrez(self, id):
        """ This may be very slow to respond FIXME
        """
        
        base_url = 'https://www.uniprot.org/uploadlists/'
        params = dict()
        params['from']='P_ENTREZGENEID'
        params['to']='ID'
        params['format']='tab'
        params['query']=id
    
        data = urlencode(params)
        data = data.encode('utf-8')
    
        try:
            req = Request(base_url, data)
        except HTTPError:
            print('Connection failed.')
    
        with urlopen(req) as f:
            response = f.read()
        rs = response.decode('utf-8')
        # uniprot returns a formatted string of '\t's and '\n's. 
        # clean it up:
        rs = rs.replace('\n', ' ').split('\t') 
        rs = [s[:-4] for s in rs]
        rs = rs[2:]
        rs = [s.strip() for s in rs]
        return rs

if __name__ == '__main__':
    import argparse
    import random
    from pubmed_api import PubMedAPI, PubMedSummary
    from uniprot_api import UniProt_API
    from stringdb_api import StringDB_API
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--term', help='Search term')
    args = parser.parse_args()

    gene_list = ['TP53', 'TNF', 'UBC', 'EGFR', 'VEGFA', 'TGFB1', 'APOE', 
                'IL6', 'TGFB1', 'MTHFR', 'ESR1', 'AKT1', 'NFKB1', 'IL10', 'ACE', 'BRCA1']

    def run(vars):
        gene_id_list = EntrezAPI().search_gene(vars)
        gene_id = random.choice(gene_id_list['IdList'])
        pmid_id_list = EntrezAPI().search_pubmed(vars)
        pmids = pmid_id_list['IdList'][:2]
        print (pmids)

        def print_json(pm):
            return_dict = dict()
            return_dict['PMID'] = pm.pmid
            return_dict['Title'] = pm.truncate_title()
            return_dict['Author'] = pm.first_author
            return_dict['Journal'] = pm.journal
            return_dict['Abstract'] = pm.truncate_abstract()
            return_dict['Citation'] = pm.cite
            return_dict['Url'] = pm.pm_url
            print (json.dumps(return_dict))

        for p in pmids:
            pms = PubMedSummary(p) # Entrez will throttle if too many requests
            pm = PubMedAPI(pms)
            if pm:
                print_json(pm)

    if (args.term):
        vars = args.term
        run(vars)
    else: 
        vars = random.choice(gene_list)
        run(vars)