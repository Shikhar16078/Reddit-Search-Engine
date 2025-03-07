from flask import Flask, render_template, request

app = Flask(__name__)

def search_lucene(query):
    # Placeholder function to search Lucene index
    return [f"Lucene result for: {query}"]

def search_bert(query):
    # Placeholder for BERT-based search (to be implemented).
    return [{"message": "BERT search is not implemented yet"}]

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        query = request.form['query']
        index_type = request.form['index_type']
        
        if index_type == 'lucene':
            print("Luecene was Searched")
            results = search_lucene(query)
        elif index_type == 'bert':
            print("Bert was Searched")
            results = search_bert(query)
    
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)