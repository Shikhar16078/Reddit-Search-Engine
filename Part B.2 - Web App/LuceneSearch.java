import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;

import java.nio.file.Paths;
import java.io.FileReader;
import java.io.IOException;

// JSON-simple imports
import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class LuceneSearch {
    public static void main(String[] args) throws Exception {
        // Expect two arguments: topK and query (which can be multiple words)
        if (args.length < 2) {
            System.out.println("{\"error\": \"Usage: java -cp '.;[libsPath]' LuceneSearch <topK> <query>\"}");
            System.exit(1);
        }

        // 1. Load configuration from JSON (Fixed Path)
        String configPath = "./utils/config.json";  // Hardcoded path
        JSONParser jsonParser = new JSONParser();
        JSONObject config;
        try (FileReader reader = new FileReader(configPath)) {
            config = (JSONObject) jsonParser.parse(reader);
        } catch (IOException | ParseException e) {
            System.err.println("{\"error\": \"Error reading/parsing config file: " + e.getMessage() + "\"}");
            return;
        }

        // Get settings from JSON
        String indexDir = (String) config.get("indexDir");

        // 2. Get topK and query from command-line arguments
        int topK = Integer.parseInt(args[0]);
        StringBuilder queryBuilder = new StringBuilder();
        for (int i = 1; i < args.length; i++) {
            queryBuilder.append(args[i]).append(" ");
        }
        String queryStr = queryBuilder.toString().trim();

        // 3. Open the index and perform the search
        FSDirectory directory = FSDirectory.open(Paths.get(indexDir));
        DirectoryReader reader = DirectoryReader.open(directory);
        IndexSearcher searcher = new IndexSearcher(reader);

        // Use the StandardAnalyzer and search in the "Body" field (adjust if needed)
        StandardAnalyzer analyzer = new StandardAnalyzer();
        QueryParser parser = new QueryParser("Body", analyzer);
        Query query = parser.parse(queryStr);

        TopDocs results = searcher.search(query, topK);

        // 4. Build JSON output
        JSONObject output = new JSONObject();
        output.put("totalHits", results.totalHits.value);
        JSONArray resultsArray = new JSONArray();

        for (ScoreDoc sd : results.scoreDocs) {
            Document doc = reader.document(sd.doc);
            JSONObject docJson = new JSONObject();
            docJson.put("score", sd.score);
            docJson.put("URL", doc.get("URL"));
            docJson.put("Title", doc.get("Title"));
            docJson.put("Body", doc.get("Body"));
            docJson.put("Comments", doc.get("Comments"));
            resultsArray.add(docJson);
        }

        output.put("results", resultsArray);

        // 5. Print JSON output to stdout
        System.out.println(output.toJSONString());

        reader.close();
    }
}
