#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# Class to retrieve, parse and format entries from UNIPROT
#------------------------------------------------------------------------------

# API Documentation: https://www.uniprot.org/help/api
# API Examples: https://www.uniprot.org/help/api_retrieve_entries

import json, re
from requests import get
from requests.exceptions import RequestException
import xmltodict
from orderedset import OrderedSet
from contextlib import closing

class UniProt_API(object):
    """USAGE (from app root):
    uni = UniProt_API(args.term)
    resp = uni.make_request_txt()
    terms = uni.extract_txt(resp)
    tags = uni.filter_tags(terms)
    print (json.dumps(tags))
    """

    def __init__(self, term, ext='.txt'):
        self.base = 'https://www.uniprot.org/uniprot/'
        self.extension = ext
        self.term = term
        self.url = self.base + term + self.extension

    def make_request_xml(self):
        """ Handling the returned content as xml is a bear. 
        """
        #print (self.url)
        try:
            with closing(get(self.url, stream=True)) as resp: #returns b`xml`
                if self.is_good_enough_xml(resp):
                    return resp.content
                else:
                    return None
        except RequestException as e:
            print('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def make_request_txt(self):
        """ Handling the returned content as text is easier. 
        """
        #print (self.url)
        try:
            with closing(get(self.url, stream=True)) as resp: #returns b`txt`
                if self.is_txt(resp):
                    return resp.content.decode("utf-8")
                else:
                    return None
        except RequestException as e:
            print('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def is_txt(self, resp):
        return True # this is not a test!

    def is_good_enough_xml(self, resp):
        """
        Returns True if response looks like XML, otherwise False.
        """
        content_type = resp.headers['Content-Type'].lower()
        
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('xml') > -1)
    
    def parse_xml_response(self, response):
        """ 
        """
        xml_dict = xmltodict.parse(response)
        return xml_dict['uniprot']['entry']['dbReference'] # this is a mess.

    def extract_xml(self, xml_list):
        """ The best I can do is extract a few matching Ref's. 
        Highly nested structure. Need XPath or something. 
        """
        craziness = dict()
        for i in range(len(xml_list)):
            if xml_list[i]['@type'] == 'EMBL':
                craziness['EMBL']=(xml_list[i]['@id'])
            elif xml_list[i]['@type'] == 'RefSeq':
                craziness['RefSeq']=(xml_list[i]['@id'])
            elif xml_list[i]['@type'] == 'Ensembl':
                craziness['Ensembl']=(xml_list[i]['@id'])
            elif xml_list[i]['@type'] == 'OrthoDB':
                craziness['OrthoDB']=(xml_list[i]['@id'])
            elif xml_list[i]['@type'] == 'PROSITE':
                craziness['PROSITE']=(xml_list[i]['@id'])
            elif xml_list[i]['@type'] == 'Pfam':
                craziness['Pfam']=(xml_list[i]['@id'])
        return craziness

    def extract_txt(self, resp):
        """ I love text!
        """
        txt_l = list()
        tags_dict = dict()
        li = resp.split('\n') # create a list
        for txt in li:
            if (re.search(r'^ID', txt)):
                tags_dict['ID'] = txt[5:].split()[0]
            elif (re.search(r'^DE', txt)):
                tags_dict['SubName'] = txt[5:].split(',')[0]
                #print (txt[5:].split(',')[0])
            elif (re.search(r'^DR', txt)):
                txt_l.append(txt[5:].split(';')[:2])
                #print (txt[5:].split(';')[:2])
        for item in txt_l:
            try:
                tags_dict[item[0]] = item[1].strip()
            except KeyError: # repeated elements, i.e. GO terms, grab just one
                pass
        return tags_dict

    def filter_tags(self, tags_dict):
        filtered_tags = dict()
        white_list = ['ID','EMBL','RefSeq','MaxQB', 'PeptideAtlas','ChEMBL','DrugBank', 'PIRSF',
                    'Ensembl','GeneID', 'KEGG','HGNC','MIM','KO','Reactome','GO','Pfam',
                    'OrthoDB','SMART','PROSITE','PRIDE', 'ProteomicsDB', 'HOGENOM', 'PANTHER']
        for tag in white_list:
            try:
                filtered_tags[tag] = tags_dict[tag]
            except KeyError:
                pass
        return filtered_tags 


if __name__ == '__main__':
    import argparse
    import random
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--term', help='Search term')
    args = parser.parse_args()

    uniprot_id_list = ['B4DNQ5_HUMAN', 'B4DVM1_HUMAN', 'B5MC21_HUMAN', 
                        'IL6_HUMAN', 'Q75MH2_HUMAN']    
    if (args.term):
        uni = UniProt_API(args.term)
        resp = uni.make_request_txt()
        terms = uni.extract_txt(resp)
        #response = uni.make_request_xml()
        #xml_list = uni.parse_xml_response(response)
        #done = uni.extract_xml(xml_list)
        tags = uni.filter_tags(terms)
        print (json.dumps(tags))
    else:
        arg = random.choice(uniprot_id_list)
        uni = UniProt_API(arg)
        resp = uni.make_request_txt()
        terms = uni.extract_txt(resp)
        #response = uni.make_request_xml()
        #xml_list = uni.parse_xml_response(response)
        #done = uni.extract_xml(xml_list)
        tags = uni.filter_tags(terms)
        print (json.dumps(tags))