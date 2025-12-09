# Gene-Genie

A web API and client for aggregating genomic information from multiple data sources.

## Overview

Imagine if every appliance you purchased came with its own unique power cord requiring custom wiring to fit your outlets. Instead, appliances are designed to plug into standardized outlets — no special knowledge required. This is what an API accomplishes for data.

Genomics data presents a particular challenge: extreme variability in both the data itself and the formats used to represent it. Gene-Genie addresses this by consolidating information from multiple API sources into a unified interface, allowing you to query and cross-reference genomic databases without navigating their underlying complexity.

**Data Sources:**

- **Entrez** — Access to PubMed, PMC, Gene, and Nuccore databases
- **String-db.org** — Protein annotations and network interactions
- **UniProt** — Resource ID tags and cross-references
- **GenomeWeb** — Genomics news and articles

## Features

- Search genes by name and retrieve functional annotations
- Cross-reference identifiers across multiple databases
- Fetch related articles from PubMed
- Display protein-protein interaction networks
- Tag cloud visualization of database cross-references

## Architecture

The project consists of two components:

- **API Layer** — Flask-based REST API that wraps external genomics data sources
- **Web Client** — Flask application with a search interface styled using [Bulma](https://bulma.io)

> **Note:** A migration to FastAPI is planned. See [Roadmap](#roadmap) for details.

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/gene_genie.git
cd gene_genie

# Create and activate virtual environment
python3 -m venv venv
source ./venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running Locally

```bash
cd gene_genie
source ./venv/bin/activate

export FLASK_APP=gene_genie.py
export FLASK_ENV=development

flask run -h localhost -p 8000
```

The web client will be available at `http://localhost:8000/`.

### Web Client

The web client provides a search interface for querying genomic data:

**Search Page**

![Search page](./images/search.png)

- **Header** — Navigation with link to home
- **Search** — Gene name entry form
- **Results** — Display area for query results

**Results Page**

![Results page](./images/results.png)

- **Annotations** — Functional annotations from String-db.org
- **Tags** — Cross-reference IDs to external databases
- **Related Articles** — Publications from PubMed
- **Interaction Graph** — Protein network visualization (when available)

## API Reference

| HTTP Method | Endpoint | Description |
|-------------|----------|-------------|
| POST | `/api/v1.0/stringdb/annotation/<term>` | Retrieve annotation from String-db.org |
| POST | `/api/v1.0/stringdb/annotations/<term>` | Retrieve multiple annotations from String-db.org |
| POST | `/api/v1.0/uniprot/<term>` | Retrieve resource ID tags from UniProt |
| GET | `/api/v1.0/pubmed/summary/<pmid>` | Retrieve summary article from PubMed |
| GET | `/api/v1.0/genomeweb/article/<gwid>` | Retrieve single news item from GenomeWeb |
| GET | `/api/v1.0/genomeweb/articles/` | Retrieve multiple news items from GenomeWeb |

### Example Requests

```bash
# String-db annotations
curl -i http://localhost:8000/api/v1.0/stringdb/annotation/BRCA1
curl -i http://localhost:8000/api/v1.0/stringdb/annotations/BRCA1

# UniProt cross-references
curl -i http://localhost:8000/api/v1.0/uniprot/BRCA1

# PubMed article summary
curl -i http://localhost:8000/api/v1.0/pubmed/summary/31411802

# GenomeWeb news
curl -i http://localhost:8000/api/v1.0/genomeweb/article/1
curl -i http://localhost:8000/api/v1.0/genomeweb/articles/
```

### Example Responses

**UniProt cross-references** (`/api/v1.0/uniprot/BRCA1`):

```json
{
  "EMBL": "AF355273",
  "GO": "GO:0016567",
  "ID": "Q90Z51_CHICK",
  "KEGG": "gga:373983",
  "KO": "K10605",
  "PROSITE": "PS50089",
  "Pfam": "PF00097",
  "Reactome": "R-GGA-351433",
  "RefSeq": "NP_989500.1",
  "SMART": "SM00184"
}
```

**PubMed summary** (`/api/v1.0/pubmed/summary/<pmid>`):

```json
{
  "PMID": "31411802",
  "Title": "BRCA mutation frequency and clinical features of ovarian...",
  "Author": "Bu H",
  "Journal": "J Obstet Gynaecol Res",
  "Abstract": "Subjects with germline BRCA1/2 mutations (gBRCAm) have...",
  "Citation": "Bu H - J Obstet Gynaecol Res",
  "Url": "http://www.ncbi.nlm.nih.gov/pubmed/31411802"
}
```

**GenomeWeb article** (`/api/v1.0/genomeweb/article/<gwid>`):

```json
{
  "feature_items": [
    {
      "date": "Aug 20, 2019",
      "link": "USPSTF Formalizes Slightly Expanded BRCA Screening Recommendations",
      "id": 1
    }
  ]
}
```

## User Stories

These scenarios illustrate how Gene-Genie serves different users in a genomics workflow.

### Translate Gene IDs Across Databases

A developer building a bioinformatics pipeline needs to map an Entrez GeneID to corresponding identifiers in UniProt, KEGG, and other databases. Rather than querying each resource separately, she calls the UniProt endpoint with a gene name and receives a unified set of cross-references.

```bash
curl -i http://localhost:8000/api/v1.0/uniprot/BRCA1
```

### Retrieve Related Literature

A graduate student researching a specific gene wants to find recently published articles. Using a PubMed ID obtained from previous results, he retrieves article metadata including title, authors, abstract, and a direct link to the publication.

```bash
curl -i http://localhost:8000/api/v1.0/pubmed/summary/31411802
```

### Explore Interaction Networks

The same student recalls that BRCA1 interacts with other genes as part of a network. The String-db endpoint returns functional annotations and can visualize protein-protein interaction networks, helping clarify the gene's role in broader biological pathways.

```bash
curl -i http://localhost:8000/api/v1.0/stringdb/annotations/BRCA1
```

### Access Genomics News

A non-technical user wants to learn more about genomics in the news. The GenomeWeb endpoint provides access to curated articles, making current developments accessible without requiring domain expertise.

```bash
curl -i http://localhost:8000/api/v1.0/genomeweb/articles/
```

## Deployment

### Cloud Deployment (AWS EC2)

```bash
# Install dependencies on EC2 instance
sudo apt-get install python3-venv

# Clone and set up the project
git clone https://github.com/<your-username>/gene_genie.git
cd gene_genie
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt

# Run the application
./run.sh
```

The application will be accessible at `http://<your-ec2-public-ip>:8000/`.

> **Tip:** For production deployments, consider using Gunicorn with Nginx as a reverse proxy.

## Development

### Running API Modules Directly

Individual API modules can be run standalone for testing and development:

```bash
source ./venv/bin/activate

# Entrez API
./app/api/entrez_api.py

# String-db API
./app/api/stringdb_api.py

# UniProt API
./app/api/uniprot_api.py

# PubMed API
./app/api/pubmed_api.py
```

**GenomeWeb API** (interactive):

```python
from app.api import genome_web_api

gw_api = genome_web_api.GenomeWebAPI()
items = gw_api.fetch()
print(items)
```

## Roadmap

**Framework Migration:**
- [ ] Migrate from Flask to FastAPI
- [ ] Add OpenAPI/Swagger documentation (automatic with FastAPI)

**Async & Performance:**
- [ ] Implement async support for concurrent API requests
- [ ] Add Celery task queue with Redis backend for request scheduling
- [ ] Implement Ajax for browser-based async calls
- [ ] Add response caching

**Infrastructure:**
- [ ] Containerize with Docker
- [ ] Add Docker Compose for local development

**Testing & Quality:**
- [ ] Add unit tests (expand Flask-Testing coverage)
- [ ] Add integration tests for external API endpoints
- [ ] Set up CI/CD pipeline

## License

MIT License