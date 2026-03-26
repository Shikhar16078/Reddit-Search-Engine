# Reddit Search Engine 🔍

## 👀 Preview

[Reddit Search Engine - Demo](https://github.com/user-attachments/assets/4279e58d-62dd-4f19-ab21-06fb73df5e67)

---

## 🚀 Overview

This project was built to study and compare different search approaches on Reddit data rather than create one fully automated search product. The system is split into separate stages so that each part of the pipeline can be developed, tested, and evaluated independently.

The project supports two search modes:

- **PyLucene based search** for traditional keyword and index-driven retrieval
- **BERT based search** for semantic, meaning-aware retrieval

This setup helped us compare behavior, and retrieval quality across both approaches.

---

## ⚡ Key Features

- Reddit data crawling using Python
- Modular pipeline with separate crawling, indexing, and search stages
- Traditional search using PyLucene indexes
- Semantic search using a BERT-based model
- Web interface for querying and displaying results
- Designed to compare retrieval quality and performance across search approaches

---

## 🏗️ System Architecture

```text
[ Reddit API ]
       ↓
[ Python Crawler ]
       ↓
[ Raw Text Files ]
       ↓
[ Indexing / Search Layer ]
   ├── PyLucene Search
   └── BERT-based Search
       ↓
[ Flask Web App ]
       ↓
[ Search Results UI ]
```

---

## 🧩 Project Workflow

This project is not fully automated end to end. It works in distinct parts:

### 1. Data Crawling
A Python script crawls selected subreddits using the Reddit API and stores the collected data as text files.

### 2. Indexing
The crawled text data is processed and prepared for search:
- PyLucene creates searchable index files for fast retrieval
- BERT based search uses semantic representations to support meaning-aware matching

### 3. Search UI
A Flask based web interface allows users to enter queries and view retrieved results from the search system.

---

## 🧠 Search Approaches

### 1. PyLucene Search
- Based on traditional information retrieval
- Uses indexed data for fast lookup
- Performs well for direct keyword matching
- More efficient in terms of speed and retrieval time

### 2. BERT Based Search
- Uses semantic understanding instead of only exact keyword overlap
- Better at understanding intent and contextual meaning
- More useful when the query and the document express similar ideas using different words

---

## 📂 Project Structure

```text
.
├── crawler/                # Python scripts for crawling subreddit data
├── indexer/                # Indexing logic for search pipeline
├── app.py                  # Flask web application
├── LuceneSearch.java       # PyLucene / Lucene-based search logic
├── templates/              # HTML templates for UI
├── static/                 # CSS and frontend assets
├── dependencies/           # Required Java libraries and related files
```

---

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Shikhar16078/Reddit-Search-Engine
cd Reddit-Search-Engine
```

### 2. Run the crawler

```bash
python crawler.py
```

This step collects subreddit data and stores it as text files.

### 3. Set up dependencies

Make sure the required dependencies for the search components are available.

For the Lucene based search, place the required `.jar` files inside the `dependencies/` directory.

### 4. Build the indexing/search components

Compile the Lucene search component:

```bash
javac -cp ".:dependencies/*" LuceneSearch.java
```

### 5. Run the web app

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## ⚠️ Important Notes

- This is a modular project and each stage is run separately
- The crawler, indexing step, and UI are independent parts of the workflow
- Search will not work unless the data has already been crawled and prepared
- The Lucene based component requires the correct Java dependencies to be present

---

## 💡 What We Learned

Building and comparing both search approaches gave us a practical understanding of the tradeoffs between traditional retrieval and semantic search.

### BERT performed better in semantic understanding
BERT was better at handling queries where the wording in the search input did not exactly match the wording in the stored Reddit posts. It could capture intent and contextual similarity more effectively, which made it stronger for natural language style queries.

### PyLucene was faster and more efficient
PyLucene performed faster because it relies on prebuilt indexes for retrieval. This makes keyword based search highly efficient and scalable for quick lookups, especially when response speed is important.

### Different search systems solve different needs
One of the biggest takeaways from this project was that there is no single best search method for every scenario:
- If speed and exact matching matter most, PyLucene is a strong choice
- If semantic understanding and query intent matter more, BERT gives better results

### System design matters as much as the model
We also learned that a good search system is not only about the retrieval model. Data preparation, indexing strategy, modular design, and a usable interface all play a big role in how effective the overall system feels.

---

## 📈 Future Improvements

- Automate the full pipeline from crawling to querying
- Add side by side comparison of results from both search modes
- Improve semantic ranking and evaluation metrics
- Support larger datasets and more subreddit sources
- Deploy the application for public access

---

## ⭐ Why This Project Matters

This project demonstrates both systems thinking and applied machine learning. It combines data collection, indexing, retrieval, and interface design into one workflow while also comparing traditional and modern approaches to search. It reflects not just the ability to build a search system, but also the ability to evaluate tradeoffs between performance and semantic quality.
