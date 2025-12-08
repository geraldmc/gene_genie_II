# What is this?

This repository contains project components for `Gene-Genie`.

### Intro

Genomics APIs represent an evolving set of protocols that assist developers in managing the plethora of data sources and in building more interoperable applications. Due to the expanding volume and diversity of genomics data, Application Programming Interfaces (APIs) have been developed to provide more secure and predictable access to a wider variety of applications and platforms.

For this project I've built a web API and web client site to aggregate genomic information from multiple API sources. An example data provider is Entrez where access to PubMed, PMC, Gene, and Nuccore are provided in API form.

# Gene Genie - API and Client

### Requirements
This project consists of two parts - an API and a web client. The client runs as a Flask app on AWS with API functions serving as primary endpoints. The following instructions are supplied to build the app and test:

#### Build with `venv` on EC2:

```bash
    $ apt-get install python3-venv
    (clone repository from Github)
    $ python3 -m venv venv
    $ source ./venv/bin/activate
    $ (venv) cd [root]/gmccoll2_final/gene_genie
    $ (venv) pip install -r ../requirements.txt
```
#### Run app locally:
```bash
    $ cd [root]/gmccoll2_final/gene_genie
    $ source ./venv/bin/activate
    $ (venv) export FLASK_APP=gene_genie.py 
    $ (venv) export FLASK_ENV=development 
    $ (venv) flask run -h localhost -p 8000
```
#### Run on Amazon EC2:
```bash
    (login to EC2 per instructions, type the word 'final' once logged in)
    $ final
    $ ./run.sh
```
### Gene-Genie `Web Client`:
The`Gene Genie`web client is a simple Flask app used to demonstrate results fom the API. It has a search view and a result. The pages have been designed using the CSS framework [Bulma](http://bulma.io).

The app entry page is here:

http://35.174.60.242:8000/

This url renders an `index` page:

![image info](./images/search.png)

1. Header - Always displayed, contains a link back to the index page on upper left. 
2. Hero - yes.
3. Account - Stub for implementing accounts.
4. Search - Main search term entry form.
5. Results -  Area of the page where results will be displayed.
6. Footer - right.

The app `search` page is accessible only through the app. 

This url renders an search results page:

![image info](./images/results.png)

1. Annotations - provided by String-db.org.
2. Tags - These are reference id translations to many other database resources.
3. Related articles - Articles provided by Pubmed. Displays only one but can have many more. 
4. Depending on latency, the tag cloud may be replaced by a network interaction graph.  

----
#### __Note__: The app runs on Amazon EC2 with a non-static IP that will change on each restart. The server will run continuously from 08/21/2019 to 08/25/2019.
----


### Gene-Genie `API Spec:`

| HTTP Method | URI                                         | Action                                |
|-------------|---------------------------------------------|---------------------------------------|
| POST         | http://[host]:8000/api/v1.0/stringdb/annotation/<string:term>    | Retrieve annotation from String-db.org. |
| POST         | http://[host]:8000/api/v1.0/stringdb/annotations/<string:term>          | Retrieve multiple annotations from String-db.org.         |
| POST         | http://[host]:8000/api/v1.0/uniprot/<string:term>    | Retrieve resource id tags from UniProt. |
| GET         | http://[host]:8000/api/v1.0/pubmed/summary/<int:pmid>    | Retrieve summary article from PubMed. |
| GET         | http://[host]:8000/api/v1.0/genomeweb/article/<int:gwid>    | Retrieve single news item from genomeweb.com. |
| GET         | http://[host]:8000/api/v1.0/genomeweb/articles/         | Retrieve multiple news items from genomeweb.com.         |

### To Test:

```bash

    $ curl -i <host>:8000/api/v1.0/stringdb/annotation/BRCA1
    $ curl -i <host>:8000/api/v1.0/stringdb/annotations/BRCA1
    $ curl -i <host>:8000/api/v1.0/uniprot/BRCA1
    $ curl -i <host>:8000/api/v1.0/pubmed/summary/31411802
    $ curl -i <host>:8000/api/v1.0/genomeweb/article/1
    $ curl -i <host>:8000/api/v1.0/genomeweb/articles/ 
```

### Example (should work through 08/25):

```bash
    $ curl -i http://35.174.60.242:8000/api/v1.0/stringdb/annotation/BRCA1
    $ curl -i http://35.174.60.242:8000/api/v1.0/stringdb/annotations/BRCA1
    $ curl -i http://35.174.60.242:8000/api/v1.0/uniprot/BRCA1
    $ curl -i http://35.174.60.242:8000/api/v1.0/pubmed/summary/31411802
    $ curl -i http://35.174.60.242:8000/api/v1.0/genomeweb/article/1
    $ curl -i http://35.174.60.242:8000/api/v1.0/genomeweb/articles/ 
```

### Run API directly from project root:
```bash
    $ cd [root]/gmccoll2_final/gene_genie
    $ source ./venv/bin/activate
```
#### entrez_api:
```bash
    $ (venv) ./app/api/entrez_api.py
```
#### stringdb_api:
```bash
    $ (venv) ./app/api/stringdb_api.py
```
#### uniprot_api:
```bash
    $ (venv) ./app/api/uniprot_api.py
 ```   
#### pubmed_api:
```bash
    $ (venv) ./app/api/pubmed_api.py
```
### genome_web_api:
```bash
    $ (venv)  from app.api import genome_web_api
    $ (venv)  gw_api = genome_web_api.GenomeWebAPI()
    $ (venv)  items = gw_api.fetch()
    $ (venv)  print(items)
```