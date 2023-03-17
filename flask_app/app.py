from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from flask import Flask, render_template, request
from transformers import pipeline
from sentence_transformers import SentenceTransformer

app = Flask(__name__)


model_name = "deepset/roberta-base-squad2"

nlp = pipeline('question-answering', model=model_name,
               tokenizer=model_name, padding=True, truncation=True)

# Load the sentence transformer model
model = SentenceTransformer('sentence-transformers/msmarco-MiniLM-L-12-v3')

# Define a retry strategy for the Elasticsearch client
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "POST"],
    backoff_factor=1
)

adapter = HTTPAdapter(max_retries=retry_strategy)

# Initialize the Elasticsearch client with the retry strategy
es = Elasticsearch(
    [{'host': 'elasticsearch', 'port': 9200}],
    connection_class=RequestsHttpConnection,
    max_retries=3
)
es.transport.connection_pool.adapter = adapter



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        question = request.form["question"]

        # Compute the question embedding
        question_embedding = model.encode(
            question, convert_to_tensor=True, show_progress_bar=False).tolist()

        index_name = 'documentation_files'

        query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": question_embedding}
                    }
                }
            },
            "size": 1
        }
        response = es.search(index=index_name, body=query)
        passages = [hit['_source'] for hit in response['hits']['hits']]

        answers = []
        for passage in passages:
            QA_input = {
                'question': question,
                'context': passage['title'] + ' ' + passage['content']
            }
            answer = nlp(QA_input)['answer']

            answers.append([answer, passage])

        return render_template("index.html", question=question, answers=answers)
    else:
        return render_template("index.html", question=None, answers=None)


if __name__ == "__main__":
    app.run(debug=True)
