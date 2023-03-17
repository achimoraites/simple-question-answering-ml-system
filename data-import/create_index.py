from elasticsearch import Elasticsearch

# Initialize Elasticsearch client
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Create an index with the appropriate mapping
mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "url": {"type": "keyword"},
            "paragraph_id": {"type": "integer"},
            "content": {"type": "text"},
            "embedding": {"type": "dense_vector", "dims": 384}  # Adjust the dims based on the model output dimension
        }
    }
}

es.indices.create(index="documentation_files", body=mapping, ignore=400)