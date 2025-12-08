#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# Class to retrieve, parse and format a Pubmed article 
#------------------------------------------------------------------------------

# API Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25501/
# API Examples: https://www.ncbi.nlm.nih.gov/books/NBK25498/

import datetime
import re, json
from functools import reduce
from collections import OrderedDict
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen

from Bio import Entrez
import xmltodict

class PubMedAPI(object):
    """USAGE (from app root):
    >> from app.api.pubmed_api import PubMedAPI, PubMedSummary
    >> pms = PubMedSummary(31412004) # pmid arg required
    >> pm = PubMedAPI(pms)
    >> summary = pms.get_pubmed_summary(31412004)
    >> json.dumps(summary[0])
    """

    def __init__(self, pubmed_summary):
        """
        """
        self.summary = pubmed_summary.summary
        self.pmid = self.summary.get('Id')
        self._author_list = self.summary.get('AuthorList')
        self.authors = ", ".join(self._author_list)
        self.first_author = self._author_list[0]
        self.issue = self.summary.get('Issue')
        self.journal = self.summary.get('Source')
        self.pages = self.summary.get('Pages')
        xml_dict = self.get_pubmed_abstract_xml()
        self.abstract = self.parse_abstract(xml_dict)
        self.pm_url = 'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(self.pmid)
        self.title = self.summary.get('Title')
        self.volume = self.summary.get('Volume')
        self.set_year(xml_dict)
        self.set_cite()

    def get_pubmed_abstract_xml(self):

        url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/' \
            'efetch.fcgi?db=pubmed&rettype=abstract&id={}' \
            .format(self.pmid)
        try:
            response = urlopen(url)
        except URLError:
            xml_dict = ''
        else:
            xml = response.read().decode()
            xml_dict = xmltodict.parse(xml)
        return xml_dict
            

    def set_abstract(self, xml_dict):
        """
        If the summary has an abstract, get it. It may not. FIXME
        """
        if self.summary.get('HasAbstract') == 1 and xml_dict:
            self.abstract = self.parse_abstract(xml_dict)
        else:
            self.abstract = ''

    def parse_abstract(self, xml_dict):
        """
        WHAT A HEADACHE!
        Parse a PubMed XML str/dict/list and get the abstract if possible.
        Traverse a path through the XML i.e. '_path'.
        To Test:
        31404966 is a dict
        31409076 is a str
        31411802 is a list
        """
        # for each entry in key_path, get the next element until done.
        _path = ['PubmedArticleSet', 'PubmedArticle', 'MedlineCitation','Article', \
                    'Abstract', 'AbstractText']
        
        # `abstract_xml` is result of fetching last element in _path.
        try:
            abstract_xml = reduce(dict.get, _path, xml_dict)
        except TypeError:
            abstract_xml = '...reference abstract empty...'
        
        paragraphs = [] # possibly more than one...

        if isinstance(abstract_xml, str): # FIXME
            paragraphs.append(abstract_xml)
            #print ('Got a dict as arg to parse_abstract...')
        elif isinstance(abstract_xml, dict):
            #print ('Got a dict as arg to parse_abstract...')
            if '#text' in abstract_xml:
                paragraphs.append(abstract_xml['#text'])
        elif isinstance(abstract_xml, list):
            section = abstract_xml[0]
            if '#text' in section:
                abstract_text = section['#text']
            else: abstract_text = section
            paragraphs.append(abstract_text)
            #print ('Got a list as arg to parse_abstract...')
        else:
            raise RuntimeError("Error parsing abstract...")

        return ''.join(paragraphs)

    def truncate_abstract(self, length=350, suffix='...'):
        if len(self.abstract) <= length:
            return self.abstract
        else:
            return ' '.join(self.abstract[:length+1].split(' ')[0:-1]) + suffix

    def truncate_title(self, length=95, suffix='...'):
        if len(self.title) <= length:
            return self.title
        else:
            return ' '.join(self.title[:length+1].split(' ')[0:-1]) + suffix

    def set_year(self, xml_dict):
        """
        """
        pubdate_xml = None
        _path = ['PubmedArticleSet', 'PubmedArticle', 'MedlineCitation',
                    'Article', 'Journal', 'JournalIssue', 'PubDate']
        try:
            pubdate_xml = reduce(dict.get, _path, xml_dict)
        except TypeError:
            pass

        if isinstance(pubdate_xml, dict):
            self.year = pubdate_xml.get('Year')
        else:
            self.year = '1969'

    def set_cite(self):
        """
        Return string formatted as '{first_author} - {year} - {journal}'
        """
        citation = [self.first_author]
        citation.extend([self.year, self.journal])
        try:
            if citation is None:
                self.cite = ''
            else: self.cite = " - ".join(citation)
        except TypeError:
            self.cite = ''


class PubMedSummary(object):
    """Retrieve a single PubMed summary using PMID (e.g. '22331878', '27609417').
    """
    def __init__(self, pmid):
        """
        Set email (required by API) and retrieve the record.
        """
        Entrez.email = 'gmccoll2@jhu.edu'

        try:
            self.summary = self.get_pubmed_summary(pmid)[0]
        except HTTPError: 
            print('Received HTTP Error 429: Too Many Requests')
        except IndexError:
            pass

    def get_pubmed_summary(self, pmid):
        """Get PubMed record from PubMed ID."""
        handle = Entrez.esummary(db="pubmed", id=pmid)
        try:
            summary = Entrez.read(handle)
        except RuntimeError:
            summary = '' 
        return summary

if __name__ == '__main__':
    import argparse
    import random
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--term', help='Search term')
    args = parser.parse_args()

    pmid_list = ['31412004', '31411802', '31410930', '31409614', '31409613', 
                '31409087', '31409082', '31409081', '31409080', '31409079', 
                '31409078', '31409076', '31408251', '31407536', '31407530', 
                '31406321', '31405835', '31405066', '31404966', '31404795']
    
    def print_all(pm):
        print(pm.truncate_title())
        print(pm.first_author)
        print(pm.journal)
        print(pm.truncate_abstract())
        print(pm.pm_url)
        print(pm.cite)

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

    if (args.term):
        pms = PubMedSummary(args.term)
        pm = PubMedAPI(pms)
        #print_all(pm)
        print_json(pm)
    else: 
        arg = random.choice(pmid_list)
        pms = PubMedSummary(arg)
        pm = PubMedAPI(pms)
        #print_all(pm)
        print_json(pm)

''' GUTTER --------------------------------------------------------------------

'''