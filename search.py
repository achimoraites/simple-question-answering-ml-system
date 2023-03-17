from elasticsearch import Elasticsearch

# Initialize the Elasticsearch client
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Define the index you want to query
index_name = 'markdown_files'

# Define the question
question = "What is the cms module?"

# Define the query
query = {
    "query": {
        "simple_query_string": {
            "query": question,
            "default_operator": "and",
            "fields": ["title", "content"]
        }
    }
}

# Execute the query and get the results
response = es.search(index=index_name, body=query)

# Print the number of hits (matching documents)
print(f"Found {response['hits']['total']['value']} documents")

# Print the documents
for hit in response['hits']['hits']:
    print(f"Document ID: {hit['_id']}")
    print(f"Document Score: {hit['_score']}")
    print(f"Document Title: {hit['_source']['title']}")
    print(f"Document Content:\n{hit['_source']['content']}\n")
