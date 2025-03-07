import subprocess
import json
from flask import Flask, render_template, request

app = Flask(__name__)

def search_lucene(query, top_k):
    # Path to your config JSON file (adjust as needed)
    config_path = r"C:\Users\shikh\Desktop\IR Project\Reddit-Search-Engine\Part B.2 - Web App\utils\config.json"
    
    # Directory containing your LuceneSearch.class file
    class_dir = r"C:\Users\shikh\Desktop\IR Project\Reddit-Search-Engine\Part B.2 - Web App\utils"
    
    lucene_search_class = "LuceneSearch"  # If not in any package
    
    # Build the command to run your Java program.
    # The -cp argument now includes the class directory and your libs folder.
    command = [
        "java",
        "-cp",
        f"{class_dir};C:\\lucene\\libs\\*",
        lucene_search_class,
        config_path,
        str(top_k),
        query  # Pass the entire query as a single argument
    ]
    
    try:
        # Run the Java program and capture output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return {"error": "Error executing Java program", "details": result.stderr}
        
        # Parse the JSON output from the Java program
        output = result.stdout.strip()
        return json.loads(output)
    except Exception as e:
        return {"error": "Exception occurred", "details": str(e)}


@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == 'POST':
        query = request.form['query']
        top_k = request.form.get('top_k', 10)  # top_k value from the UI (default: 10)
        index_type = request.form['index_type']
        
        if index_type == 'lucene':
            print("Lucene was Searched")
            results = search_lucene(query, top_k)
        elif index_type == 'bert':
            print("BERT was Searched")
            results = {"message": "BERT search is not implemented yet"}
    
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)