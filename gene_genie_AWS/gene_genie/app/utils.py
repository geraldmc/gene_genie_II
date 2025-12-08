# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import json
import xmltodict
from .api.pubmed_api import PubMedAPI, PubMedSummary

def get_pmid_return_object(pm):
    if (isinstance(pm, PubMedAPI)):
        print('is PubMedAPI ... ')
        return_dict = dict()
        return_dict['PMID'] = pm.pmid
        return_dict['Title'] = pm.truncate_title()
        return_dict['Author'] = pm.first_author
        return_dict['Journal'] = pm.journal
        return_dict['Abstract'] = pm.truncate_abstract()
        return_dict['Citation'] = pm.cite
        return_dict['Url'] = pm.pm_url
        return return_dict
    elif (isinstance(pm, list)):
        for p in pm:
            pmid_dict_list = list()
            return_dict = dict()
            return_dict['PMID'] = p.pmid
            return_dict['Title'] = p.truncate_title()
            return_dict['Author'] = p.first_author
            return_dict['Journal'] = p.journal
            return_dict['Abstract'] = p.truncate_abstract()
            return_dict['Citation'] = p.cite
            return_dict['Url'] = p.pm_url
            pmid_dict_list.append(return_dict)
            return pmid_dict_list
    else:
        return None

def pmid_from_entrez_dict():
    """Returns a dictionary mapping NCBI GeneIDs to NCBI PubMed_IDs
    """
    fp = './data/gene2pubmed_brief' # ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2pubmed.gz
    fp_large = './gene2pubmed' # In memory size is 8/10ths of a gigabyte!
    df = pd.read_csv(fp, sep='\t', usecols=['GeneID','PubMed_ID'])
    gene_to_pmid = dict(zip(df.GeneID,df.PubMed_ID)) # create dict
    return gene_to_pmid

def omim_from_entrez():
    """Returns a dictionary mapping NCBI GeneIDs to OMIM IDs
    Returns 17,126 entries from an original 26,371.
    
    >> omim_from_entrez_dict[3274] 
    >> 142703 (HRH2 histamine receptor H2)
    """
    fp = './data/mim2gene.txt' # https://www.omim.org/static/omim/data/mim2gene.txt
    df = pd.read_csv(fp, skiprows=4, sep='\t',
                    usecols=['# MIM Number', 'Entrez Gene ID (NCBI)'])
    df.columns = ['omim', 'ncbi'] # rename columns
    df = df[np.isfinite(df['ncbi'])] # remove NaN's from ncbi
    df['ncbi'] = df['ncbi'].astype(int) # recast ncbi as int
    ncbi_to_omim = dict(zip(df.ncbi,df.omim)) # create dict