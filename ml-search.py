import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from elasticsearch import Elasticsearch

# Load the pre-trained Transformer model and tokenizer
model_name = "distilbert-base-uncased-distilled-squad"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Initialize the Elasticsearch client
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Define the index you want to query
index_name = 'markdown_files'

# Define the question
question = "What is the cms module?"

# Define the query to find relevant documents
query = {
    "query": {
        "simple_query_string": {
            "query": question,
            "default_operator": "and",
            "fields": ["title", "content"]
        }
    },
    "size": 3  # Limit the number of documents to retrieve
}

# Execute the query and get the results
response = es.search(index=index_name, body=query)

# Extract relevant passages from the returned documents
passages = [hit['_source']['content'] for hit in response['hits']['hits']]

# Use the Transformer model to answer the question
max_answer_length = 30

for passage in passages:
    inputs = tokenizer(question, passage, return_tensors='pt', max_length=512, truncation=True)
    outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits)
    input_ids = inputs["input_ids"][0].tolist()
    answer_tokens = input_ids[answer_start:answer_end + 1]
    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)

    print(f"Passage: {passage[:200]}...")
    print(f"Answer: {answer}\n")
