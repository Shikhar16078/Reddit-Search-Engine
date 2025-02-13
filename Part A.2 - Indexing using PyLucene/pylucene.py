import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import BM25Similarity

def create_index(dir, json_file_path):
    if not os.path.exists(dir):
        os.mkdir(dir)
    store = SimpleFSDirectory(Paths.get(dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    # Define the field types for indexing
    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    textType = FieldType()
    textType.setStored(True)
    textType.setTokenized(True)
    textType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    # Open the Reddit JSON file
    with open(json_file_path, 'r') as f:
        # Read the file line by line (since each line is a JSON object)
        for line in f:
            try:
                post = json.loads(line.strip())  # Parse the JSON object

                title = post.get('title', '')
                body = post.get('body', '')
                comments = ' '.join([comment['body'] for comment in post.get('comments', [])])

                # Create a new document for each Reddit post
                doc = Document()
                doc.add(Field('Title', title, metaType))
                doc.add(Field('Body', body, textType))
                doc.add(Field('Comments', comments, textType))  # Index the body of the comments together
                writer.addDocument(doc)
            except json.JSONDecodeError:
                # If a line is not a valid JSON object, skip it
                continue

    writer.close()

def retrieve(storedir, query):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser('Body', StandardAnalyzer())
    parsed_query = parser.parse(query)

    topDocs = searcher.search(parsed_query, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "title": doc.get("Title"),
            "body": doc.get("Body"),
            "comments": doc.get("Comments")
        })
    
    for doc in topkdocs:
        print(f"Score: {doc['score']}, Title: {doc['title']}, Body: {doc['body']}, Comments: {doc['comments']}")

# Initialize Lucene VM
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# Path to your Reddit JSON .txt file
json_file_path = '/home/cs242/reddit_batch_1.txt'

# Create the index from the Reddit data file
create_index('reddit_lucene_index/', json_file_path)

# Retrieve data based on a query
retrieve('reddit_lucene_index/', 'game')
