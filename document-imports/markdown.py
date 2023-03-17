import os
from elasticsearch import Elasticsearch

# Load the Markdown file
markdown_file = 'README.md'
with open(markdown_file, 'r', encoding='utf-8') as f:
    markdown_content = f.read()

# Extract the title (assuming the first heading is the title)
title_lines = [line for line in markdown_content.splitlines() if line.startswith(('#', '##', '###', '####', '#####', '######'))]
title = title_lines[0] if title_lines else 'Untitled'

# Preprocess the data: create a document for Elasticsearch
document = {
    'file': os.path.abspath(markdown_file),
    'title': title,
    'content': markdown_content,
}
print(document)
# Index the document in Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
index_name = 'markdown_files'
doc_type = '_doc'
es.index(index=index_name, doc_type=doc_type, body=document)
