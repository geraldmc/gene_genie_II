#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# Class to retrieve, parse and format json for news sections of GenomeWeb
#------------------------------------------------------------------------------

# Web Interface: https://www.genomeweb.com/breaking-news

import os.path
from pathlib import Path
import re
import json
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup, SoupStrainer

class GenomeWebAPI(object):
    """USAGE (from app root):
    >> from app.api.pubmed_api import GenomeWebAPI
    >> gw_api = GenomeWebAPI()
    >> items = gw_api.fetch()
    >> print(items)
    """
    
    def __init__(self, DEBUG=False):
        self.url = 'https://www.genomeweb.com/breaking-news'
        self.CACHED_HTML_abs_path = Path('./app/data/genomeweb.txt').resolve()
        self.CACHED_HTML = './app/data/genomeweb.txt'
        self.DEBUG = DEBUG

    def simple_get(self, url):
        """
        Get contents of url using HTTP GET. If the response is HTML/XML
        return text, otherwise return None.
        """
        try:
            with closing(get(self.url, stream=True)) as resp: #returns `bytes`
                if self.is_good_enough(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            self.log('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def is_good_enough(self, resp):
        """
        Returns True if response looks like HTML, otherwise False.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('html') > -1)

    def log(self, e):
        """
        Broke dat.
        """
        print(e)

    def write_outfile(self, fh, raw_html):
        with open(fh, 'w') as output:
            output.write(raw_html.decode("utf-8"))

    def write_json(self, data):
        with open('./app/data/data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def read_infile(self, fh):
        try:
            with open(fh) as input:  
                raw_html = input.read()
        except FileNotFoundError as fnf:
            self.log('Read Error in {0} : {1}'.format('read_infile', str(fnf))) 
        return raw_html

    def format_scan_items(self, the_scan):
        """ These are subscription only so won't work, oops...
        """ 
        urls = list()
        for item in the_scan:
            urls.append(item.contents[0])
        return urls

    def format_slugs(self, combined):
        """Prepare slugs.
        """
        dates = list()
        links = list()
        for item in combined:
            for i in item[0]:
                i = str(i).rstrip('</span>')
                dates.append(i[-12:])
            for i in item[1]:
                i = str(item)
                links.append(i[i.find('<a href'):-6])
        assert len(dates) == len(links) # sanity
        
        return (dates, links)

    def mod_fields(self, dates, links):
        """ FIXME
        """
        clean_links = list()
        p = [{'date': dates, 'link': links} for dates, links in zip(dates, links)]
        for i in enumerate(p, start=1):
            p[int(i[0]-1)]['id'] = int(i[0]) # add an ID field
        for j in p:
            # Required to construct a *complete* url to GenomeWeb ------------ FIXME ------------
            s = '<a href=' + self.url + j['link'][j['link'].find('/'):].replace('"', '') # start clean
            s = '="'.join(s.rsplit("=", 1)) # insert double-quote on left side of link
            idx = s.find('>') # find right-hand side of link
            s = list(s) # cast str as a list for the next operation
            s.insert(idx, '"') # insert double-quote on left side of link
            s = ''.join(s) # cast back again to a str
            clean_links.append(s) # add to list of clean links
        assert len(clean_links) == len(p) # are they equal?
        for idx in range(len(clean_links)): # update sub-dictionary with final links
            p[idx]['link'] = clean_links[idx]
        return p

    def fetch(self):

        dates = list()
        links = list()
        d = list()
        s = list()
        payload = list()
        the_scan = list()

        if self.CACHED_HTML_abs_path.exists():
            try:
                raw_html = self.read_infile(self.CACHED_HTML_abs_path)
            except UnboundLocalError as ubl:
                self.log('raw_html unbound in {0} : {1}'.format('fetch', str(ubl))) 
        else:
            raw_html = self.simple_get(self.url)
            self.write_outfile(self.CACHED_HTML, raw_html)

        divs = SoupStrainer('div', attrs={'class': 'views-group'})
        soup = BeautifulSoup(raw_html, "html.parser", parse_only=divs)

        for item in soup.find_all('div', 
                            attrs={'property': re.compile('datePublished')}):
            d.append(item)
        for item in soup.find_all('h3', 
                            attrs={'class': re.compile('node-title')}):
            s.append(item)

        the_scan = s[len(d):] # elements for breaking news section
        s = s[:len(s)-len(the_scan)] # all others
        assert len(s) == len(d) # sanity

        combined = zip(d[:5], s[:5])
        dates, links = self.format_slugs(combined)
        assert len(dates) == len(links)

        sub_dict = self.mod_fields(dates, links) # adds ID field, the full url
        
        final_dict = {}
        final_dict['feature_items'] = [ dic for dic in sub_dict ] # roll it up...

        if self.DEBUG:
            print(json.dumps(final_dict, indent=4)) # and serve
        else:
            return json.dumps(final_dict)

if __name__ == '__main__':
    print("--------------------------------------------------")
    print("NOTE: This must be run relative to the app root...")
    print("--------------------------------------------------")
    gw_api = GenomeWebAPI()
    items = gw_api.fetch()
    print(type(items))  
    print(items)


''' GUTTER --------------------------------------------------------------------

'''