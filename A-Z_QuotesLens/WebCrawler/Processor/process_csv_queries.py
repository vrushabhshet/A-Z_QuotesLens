import csv
import json
import os
import sys
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE_DIR, "../quotes_output.html")


# ------------------------------------------------------------
# HTML → Corpus Loader
# ------------------------------------------------------------
def load_corpus():
    """
    Parse 'quotes_output.html' and extract a normalized list of quotes.

    Output:
        articles  → list of dicts: { text, author, tags }
        documents → just the quote text (for TF-IDF)

    Supports:
        - GoodReads-style structure
        - Simplified <p> fallback format
    """
    if not os.path.exists(HTML_PATH):
        raise FileNotFoundError(f"Could not locate corpus file at: {HTML_PATH}")

    with open(HTML_PATH, "r", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp.read(), "html.parser")

    articles = []

    # --- Primary: <div class='quote'> blocks (GoodReads layout)
    for div in soup.find_all("div", class_="quote"):
        text_tag = div.find("span", class_="text")
        author_tag = div.find("span", class_="author")
        tag_group = div.find("div", class_="tags")

        if text_tag:
            quote_text = text_tag.get_text(strip=True)
            author = author_tag.get_text(strip=True) if author_tag else ""
            tags = [a.get_text(strip=True) for a in tag_group.find_all("a")] if tag_group else []
            articles.append({"text": quote_text, "author": author, "tags": tags})

    # --- Fallback: <p> block extraction
    if not articles:
        for p in soup.find_all("p"):
            stripped = list(p.stripped_strings)
            if not stripped:
                continue

            text = stripped[0]
            author = stripped[1].replace("—", "").strip() if len(stripped) > 1 else ""
            tags = []

            if len(stripped) > 2 and stripped[2].startswith("Tags:"):
                tags = [t.strip() for t in stripped[2].replace("Tags:", "").split(",")]

            articles.append({"text": text, "author": author, "tags": tags})

    if not articles:
        raise ValueError("No quotes detected inside quotes_output.html")

    documents = [item["text"] for item in articles]
    return articles, documents


# ------------------------------------------------------------
# TF-IDF Setup
# ------------------------------------------------------------
def build_tfidf(documents):
    """
    Fit a TF-IDF vectorizer and produce its matrix.
    """
    vec = TfidfVectorizer(stop_words="english")
    mat = vec.fit_transform(documents)
    return vec, mat


# ------------------------------------------------------------
# Ranking Logic
# ------------------------------------------------------------
def rank_docs(vec, matrix, query_text, top_k=3):
    """
    Compute cosine similarity between user's query and all documents.

    Returns:
        list of (doc_index, score) sorted by relevance descending.
    """
    q_vec = vec.transform([query_text])
    sim = cosine_similarity(q_vec, matrix)[0]
    ordered = sim.argsort()[::-1]  # high → low

    results = []
    for idx in ordered:
        sc = float(sim[idx])
        if sc <= 0:
            break
        results.append((idx, sc))
        if len(results) >= top_k:
            break

    return results


# ------------------------------------------------------------
# Path Normalizer
# ------------------------------------------------------------
def _resolve_path(p: str) -> str:
    return p if os.path.isabs(p) else os.path.join(BASE_DIR, p)


# ------------------------------------------------------------
# CSV Query Processor
# ------------------------------------------------------------
def process_queries_csv(input_csv, output_csv, top_k=3):
    """
    Read a CSV of queries and output ranked results.
    """
    articles, docs = load_corpus()
    vec, mat = build_tfidf(docs)

    input_csv = _resolve_path(input_csv)
    output_csv = _resolve_path(output_csv)

    with open(input_csv, "r", encoding="utf-8") as fin, open(
        output_csv, "w", encoding="utf-8", newline=""
    ) as fout:

        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=["query_id", "rank", "document_id"])
        writer.writeheader()

        for row in reader:
            q_id = (row.get("query_id") or "").strip()
            q_text = (row.get("query_text") or "").strip()
            if not q_id or not q_text:
                continue

            ranked = rank_docs(vec, mat, q_text, top_k=top_k)
            for position, (doc_id, _) in enumerate(ranked, start=1):
                writer.writerow({
                    "query_id": q_id,
                    "rank": position,
                    "document_id": str(doc_id)
                })

    print(f"CSV processed → {output_csv}")


# ------------------------------------------------------------
# JSON Query Handler (used by your UI)
# ------------------------------------------------------------
def process_query_json(query_text, top_k=5):
    """
    Rank a single query and return JSON-compatible results.
    """
    articles, docs = load_corpus()
    vec, mat = build_tfidf(docs)
    ranked = rank_docs(vec, mat, query_text, top_k=top_k)

    output = []
    for idx, score in ranked:
        q = articles[idx]
        output.append({
            "text": q["text"],
            "Authorname": q["author"],
            "tags": q.get("tags", []),
            "cosine_similarity_score": score
        })

    return output


# ------------------------------------------------------------
# CLI Mode
# ------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 process_csv_queries.py queries.csv results.csv [top_k]")
        sys.exit(1)

    in_csv = sys.argv[1]
    out_csv = sys.argv[2]
    k = int(sys.argv[3]) if len(sys.argv) >= 4 else 3

    process_queries_csv(in_csv, out_csv, top_k=k)

    # Quick verification
    quotes, docs = load_corpus()
    print(f"Loaded {len(quotes)} quotes")
    for q in quotes[:3]:
        print(q)
