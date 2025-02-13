import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json
from org.apache.lucene.store import SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, LongPoint
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause, TermQuery, PhraseQuery, WildcardQuery
from org.apache.lucene.index import Term

def create_index(index_dir, data_dir):
    """
    Index multiple Reddit JSON/TXT files from a given directory.

    :param index_dir: Path to store the Lucene index
    :param data_dir: Path containing multiple Reddit text files
    """
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    store = SimpleFSDirectory(Paths.get(index_dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    # Define field types for indexing
    metaType = FieldType()
    metaType.setStored(True)
    metaType.setTokenized(False)

    textType = FieldType()
    textType.setStored(True)
    textType.setTokenized(True)
    textType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    # Iterate over all JSON/TXT files in the directory
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if filename.endswith(".txt") or filename.endswith(".json"):
            print(f"Indexing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        post = json.loads(line.strip())

                        title = post.get('title', '')
                        body = post.get('body', '')
                        comments = ' '.join([comment['body'] for comment in post.get('comments', [])])
                        mod_date = int(post.get('mod_date', 0))  # Ensure mod_date is indexed as an integer

                        doc = Document()
                        doc.add(Field('Title', title, metaType))
                        doc.add(Field('Body', body, textType))
                        doc.add(Field('Comments', comments, textType))
                        doc.add(LongPoint("mod_date", mod_date))  # Store mod_date as a long integer
                        writer.addDocument(doc)
                    except json.JSONDecodeError:
                        continue

    writer.close()
    print("Indexing complete!")

def retrieve(storedir, query_type, **kwargs):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    boolean_query = BooleanQuery.Builder()
    
    if query_type == "boolean":
        for term, occur in kwargs.get("terms", []):  
            boolean_query.add(BooleanClause(TermQuery(Term("Body", term)), occur))
    
    elif query_type == "boosting":
        parser = QueryParser("Body", StandardAnalyzer())
        boosted_query = parser.parse(kwargs.get("query", ""))
        boolean_query.add(BooleanClause(boosted_query, BooleanClause.Occur.SHOULD))

    elif query_type == "proximity":
        phrase_query = PhraseQuery.Builder()
        for word in kwargs.get("phrase", []):
            phrase_query.add(Term("Body", word))
        phrase_query.setSlop(kwargs.get("slop", 4))
        boolean_query.add(BooleanClause(phrase_query.build(), BooleanClause.Occur.MUST))

    elif query_type == "range":
        field = kwargs.get("field", "mod_date")
        start, end = kwargs.get("range", (0, 0))
        range_query = LongPoint.newRangeQuery(field, start, end)
        boolean_query.add(BooleanClause(range_query, BooleanClause.Occur.MUST))

    elif query_type == "wildcard":
        wildcard_query = WildcardQuery(Term("Body", kwargs.get("pattern", "")))
        boolean_query.add(BooleanClause(wildcard_query, BooleanClause.Occur.MUST))

    else:
        parser = QueryParser("Body", StandardAnalyzer())
        parsed_query = parser.parse(kwargs.get("query", ""))
        boolean_query.add(BooleanClause(parsed_query, BooleanClause.Occur.MUST))

    topDocs = searcher.search(boolean_query.build(), kwargs.get("top_k", 10)).scoreDocs
    results = []

    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        result = {
            "score": hit.score,
            "title": doc.get("Title"),
            "body": doc.get("Body"),
            "comments": doc.get("Comments")
        }
        results.append(result)

        # Print search results to console
        print("\n----------------------------------------")
        print(f"Score: {result['score']}")
        print(f"Title: {result['title']}")
        print(f"Body: {result['body'][:500]}...")  # Print only first 500 chars to avoid long output
        print(f"Comments: {result['comments'][:300]}...")  # Print only first 300 chars
        print("----------------------------------------\n")

    return results

# Initialize Lucene VM
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# Directory containing multiple Reddit JSON/TXT files
data_directory = '/home/cs242/CS242-Project-Reddit/reddit_data'  # Change this to the path of your data directory

# Path to store Lucene index
index_directory = 'reddit_lucene_index/'

# Create the index for multiple Reddit files
create_index(index_directory, data_directory)

# Basic Query Example
#results = retrieve('reddit_lucene_index/', 'default', query="game")

# Boolean Query Example (AND between "ios" and "android", OR with "quick fox")
results = retrieve('reddit_lucene_index/', 'boolean', 
                   terms=[("PLMOKN", BooleanClause.Occur.MUST), 
                          ("android", BooleanClause.Occur.MUST), 
                          ("QAZWSXEDC", BooleanClause.Occur.MUST)])

# Boosting Example (boost "ios" over "android")
#results = retrieve('reddit_lucene_index/', 'boosting', query="ios^1.5 OR android")

# Proximity Search Example ("ios android" within 4 words)
#results = retrieve('reddit_lucene_index/', 'proximity', phrase=["ios", "android"], slop=4)

# Range Search Example (for date range)
#results = retrieve('reddit_lucene_index/', 'range', field="mod_date", range=(20020101, 20030101))

# Wildcard Search Example (Search for "ios*android")
#results = retrieve('reddit_lucene_index/', 'wildcard', pattern="ios*android")