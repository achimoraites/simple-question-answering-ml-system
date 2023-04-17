# Simple Question Answering ML System


This is a question and answering system that scrapes paragraphs from web pages, indexes them using Elasticsearch, and leverages the power of semantic search and natural language understanding to provide relevant answers to user queries. 


## Features
- Web scraping using Beautiful Soup
- Document indexing with Elasticsearch
- Semantic Search with result sources
- Extractive Question Answering

https://user-images.githubusercontent.com/4193340/226748890-2415ca7e-e13a-4e5e-9f82-c56a1a6408cc.mp4

## Setup

**This project built using Python 3.10.4**

```bash
python -m venv venv

# Linux / MacOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate


pip install -r requirements.txt

```

```bash
docker-compose up -d build

```

Kibana link http://localhost:5601
The Flask application should be accessible at http://localhost:5001.

## Elastic Search
The first time you will need to add the index for storing the documents

```bash
python /data-import/create_index.py
```

To import some sample pages you can run

```bash
python /data-import/webpages.py
```
