# -*- coding: utf-8 -*-

import json, random, sys
from flask import render_template
from flask import request, make_response
from flask import jsonify, abort  

from app import app
from app.api.stringdb_api import StringDB_API
from app.api.pubmed_api import PubMedAPI, PubMedSummary
from app.api.uniprot_api import UniProt_API
from app.api.entrez_api import EntrezAPI
from app.api.genome_web_api import GenomeWebAPI
from app.utils import *
from libgravatar import Gravatar

@app.route('/')
@app.route('/index')
def index():
    sdb_resp = ['','']
    uni_terms = ''  
    pmid_dict_list = dict()
    tags = ''
    user = {'username': 'Gerald'}
    return render_template('template_index.html', 
                            title='Home',
                            pmid_dict=pmid_dict_list,
                            sdb_resp=sdb_resp,
                            tags=tags, user=user)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/api/v1.0/genomeweb/article/<int:gwid>', methods=['GET'])
def get_article(gwid):
    """ Test with: 1,2,3
    """
    if request.method == 'GET':
        term = request.form
    gw = GenomeWebAPI()
    articles = json.loads(gw.fetch())
    article = [item for item in articles['feature_items'] if item['id'] == gwid]
    if len(article) == 0:
        abort(404)
    return jsonify({'article': article[0] })

@app.route('/api/v1.0/genomeweb/articles/', methods=['GET'])
def get_articles():
    if request.method == 'GET':
        term = request.form
    gw = GenomeWebAPI(term)
    articles = json.loads(gw.fetch())
    return jsonify({'articles': articles['feature_items']})

@app.route('/api/v1.0/stringdb/annotation/<string:term>', methods=['GET', 'POST'])
def get_annotation(term):
    """ Test with: 'BRCA1', 'TP53', 'ESR1'
    """
    #print(request.form, flush=True)
    if request.method == 'POST':
        term = request.form
    sdb = StringDB_API(term)
    resp = sdb.make_request_json()
    #print(resp, flush=True)
    if resp is None:
        abort(404)
    return jsonify({'string_db_single':  resp[0]})

@app.route('/api/v1.0/stringdb/annotations/<string:term>', methods=['GET', 'POST'])
def get_annotations(term):
    #print(request.form, flush=True)
    if request.method == 'POST':
        term = request.form
    sdb = StringDB_API(term)
    resp = sdb.make_request_json()
    #print(resp, flush=True)
    if resp is None:
        abort(404)
    return jsonify({'string_db_list':  resp})

@app.route('/api/v1.0/pubmed/summary/<int:pmid>', methods=['GET'])
def get_summary(pmid):
    """ Test with: 31411802, 31409614, 31407536, 31406321
    """
    print(request.args, flush=True)
    pms = PubMedSummary(pmid)
    pm = PubMedAPI(pms)
    d = get_pmid_return_object(pm)
    if len(d) == 0 or d is None:
        abort(404)
    return jsonify(d)

@app.route('/api/v1.0/uniprot/<string:term>', methods=['GET', 'POST'])
def get_uniprot(term):
    if request.method == 'POST':
        term = request.form
    gene_id_list = EntrezAPI().search_gene(term)
    gene_id = gene_id_list['IdList'][4]
    uniprot_id = EntrezAPI().get_uniprot_from_entrez(gene_id)[0]
    uni = UniProt_API(uniprot_id, '.txt')
    uni_resp = uni.make_request_txt()
    uni_terms = uni.extract_txt(uni_resp)
    tags = uni.filter_tags(uni_terms)
    return tags

@app.route('/web_search', methods = ['POST'])
def web_search():
    user = {'username': 'Gerald'}
    if request.method == 'POST':
        term = request.form
        if term == None:
            term = dict()
            term['gene_search'] == 'MTHFR' # very rude gene ...
            return ""
        else:
            # Entrez/Pubmed -------------------
            gene_id_list = EntrezAPI().search_gene(term['gene_search'])
            gene_id = random.choice(gene_id_list['IdList'])
            pmid_id_list = EntrezAPI().search_pubmed(term['gene_search'])
            pmids = pmid_id_list['IdList'][:3]
            print(pmids)
            
            # Uniprot -------------------------
            uniprot_id = EntrezAPI().get_uniprot_from_entrez(gene_id)[0]
            uni = UniProt_API(uniprot_id, '.txt')
            uni_resp = uni.make_request_txt()
            uni_terms = uni.extract_txt(uni_resp)
            tags = uni.filter_tags(uni_terms)
            
            # StringDB ------------------------
            sdb = StringDB_API(term['gene_search'])
            sdb_resp = sdb.make_request_json()

            try:
                pmid_list = list()
                for pmid in pmids:
                    pms = PubMedSummary(pmid)
                    pm = PubMedAPI(pms)
                    pmid_list.append(pm)
            except AttributeError:
                print ("Entrez is Throttling... Wait a minute and try again.")

            pmid_dict_list = get_pmid_return_object(pmid_list)

        return render_template('template_search.html', 
                                title='Results', 
                                sdb_resp=sdb_resp,
                                uni_terms=uni_terms,
                                tags=tags,
                                pmid_dict=pmid_dict_list,
                                term=term['gene_search'],
                                user=user)