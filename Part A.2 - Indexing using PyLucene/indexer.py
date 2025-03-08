import logging, sys
logging.disable(sys.maxsize)
import lucene
import os
import json
import time
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
    Index multiple Reddit JSON/TXT files from a given directory while measuring execution time.
    """
    start_time = time.time()  # Start total timing

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
                        url = post.get('url','')
                        comments = ' '.join([comment['body'] for comment in post.get('comments', [])])
                        mod_date = int(post.get('mod_date', 0))  # Ensure mod_date is indexed as an integer

                        doc = Document()
                        doc.add(Field('URL', url, metaType))
                        doc.add(Field('Title', title, metaType))
                        doc.add(Field('Body', body, textType))
                        doc.add(Field('Comments', comments, textType))
                        doc.add(LongPoint("mod_date", mod_date))  # Store mod_date as a long integer
                        writer.addDocument(doc)
                    except json.JSONDecodeError:
                        continue
    
    writer.close()
    end_time = time.time()  # End total timing
    total_runtime = end_time - start_time  # Calculate total runtime
    print(f"Total indexing completed in {total_runtime:.2f} seconds.", flush=True)

    # Save total indexing time to a file
    with open("indexing_time.txt", "w") as f:
        f.write(str(total_runtime))


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
            "url": doc.get("URL"),
            "title": doc.get("Title"),
            "body": doc.get("Body"),
            "comments": doc.get("Comments")
        }
        results.append(result)

        # Print search results to console
        print("\n----------------------------------------")
        print(f"Score: {result['score']}")
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Body: {result['body'][:500]}...")  # Print only first 500 chars to avoid long output
        print(f"Comments: {result['comments'][:300]}...")  # Print only first 300 chars
        print("----------------------------------------\n")

    return results

# Initialize Lucene VM
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# Directory containing multiple Reddit JSON/TXT files
data_directory = '/home/cs242/CS242-Project-Reddit/data'  # Change this to the path of your data directory

# Path to store Lucene index
index_directory = 'reddit_lucene_index/'

# Automatically index the Reddit data
print("\nIndexing the Reddit data...")
create_index(index_directory, data_directory)

# Choose a query type for searching
print("\nChoose a query type:")
print("1. Basic Query")
print("2. Boolean Query (AND/OR)")
print("3. Boosting Query")
print("4. Proximity Search")
print("5. Wildcard Search")

query_type = input("Enter query type (1-5): ").strip()

if query_type == "1":
    query = input("Enter search query: ").strip()
    search_args = {"query_type": "default", "query": query}

elif query_type == "2":
    term1 = input("Enter first term: ").strip()
    term2 = input("Enter second term: ").strip()
    search_args = {"query_type": "boolean", "terms": [(term1, BooleanClause.Occur.MUST), (term2, BooleanClause.Occur.SHOULD)]}

elif query_type == "3":
    query = input("Enter search query with boosting (e.g., 'ios^2.0 OR android'): ").strip()
    search_args = {"query_type": "boosting", "query": query}

elif query_type == "4":
    phrase = input("Enter phrase for proximity search (separate words by space): ").strip().split()
    slop = int(input("Enter proximity slop (distance between words): ").strip())
    search_args = {"query_type": "proximity", "phrase": phrase, "slop": slop}

elif query_type == "5":
    pattern = input("Enter wildcard pattern (e.g., 'android*life'): ").strip()
    search_args = {"query_type": "wildcard", "pattern": pattern}

else:
    print("Invalid choice! Exiting...")
    search_args = None

# Perform the search after indexing
if search_args:
    retrieve(index_directory, **search_args)

