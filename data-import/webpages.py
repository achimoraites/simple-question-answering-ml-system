import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# Initialize Elasticsearch client
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Load the sentence transformer model
model = SentenceTransformer('sentence-transformers/msmarco-MiniLM-L-12-v3')

# Define a function to fetch and parse webpages
def fetch_and_parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract webpage title
    title = soup.title.string if soup.title else "No title found"
    
    # Extract and store paragraphs as separate documents
    paragraphs = []
    for i, p in enumerate(soup.find_all('p')):
        content = p.get_text().strip()
        # Compute the paragraph embedding
        embedding = model.encode(content, convert_to_tensor=True, show_progress_bar=False).tolist()

        paragraphs.append({
            'url': url,
            'title': title,
            'paragraph_id': i,
            'content': content,
            'embedding': embedding
        })
    
    return paragraphs

# List of URLs to index
urls = [
    "https://en.wikipedia.org/wiki/Web_scraping",
    "https://en.wikipedia.org/wiki/Elasticsearch",
    "https://en.wikipedia.org/wiki/Python_(programming_language)"
]

# Index the webpages in Elasticsearch
for url in urls:
    parsed_pages = fetch_and_parse(url)
    
    for page in parsed_pages:
        # Index the paragraph as a separate document in Elasticsearch
        es.index(index='documentation_files', doc_type='_doc', body=page)
