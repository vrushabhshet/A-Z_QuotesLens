import os
import re
from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ------------------------------------------------------------------------------
# Normalizer: Clean tag names for unified matching
# ------------------------------------------------------------------------------
def normalize_tag(value: str) -> str:
    """Strip weird spaces, collapse whitespace, lowercase the tag."""
    if not isinstance(value, str):
        return ""
    cleaned = value.replace("\xa0", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.lower()


# ------------------------------------------------------------------------------
# Paths + HTML Parser
# ------------------------------------------------------------------------------
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(ROOT_PATH, "../quotes_output.html")
TEMPLATE_PATH = os.path.join(ROOT_PATH, "templates")


def parse_quotes_html(path):
    """Extract quotes, authors, tags from HTML."""
    with open(path, "r", encoding="utf-8") as fp:
        soup_obj = BeautifulSoup(fp.read(), "html.parser")

    text_list = []
    meta_list = []

    blocks = soup_obj.find_all("p")
    idx = 0
    while idx < len(blocks):
        block = blocks[idx]
        strong_tag = block.find("strong")

        if strong_tag:
            raw_quote = strong_tag.get_text(strip=True)
            if raw_quote:
                lines = list(block.stripped_strings)

                author_val = ""
                tags_val = []

                j = 1
                while j < len(lines):
                    row = lines[j].strip()
                    if row.startswith("—"):
                        author_val = row[1:].strip()
                    elif row.startswith("Tags:"):
                        extracted = row[5:].split(",")
                        tags_val = [
                            normalize_tag(t)
                            for t in extracted
                            if normalize_tag(t)
                        ]
                    j += 1

                text_list.append(raw_quote)
                meta_list.append({
                    "body": raw_quote,
                    "writer": author_val,
                    "labels": tags_val
                })

        idx += 1

    return text_list, meta_list


# ------------------------------------------------------------------------------
# Load + Prepare Data
# ------------------------------------------------------------------------------
CORPUS, METAINFO = parse_quotes_html(HTML_FILE)
if not CORPUS:
    raise RuntimeError("Failed to load quotes from HTML.")

TFIDF = TfidfVectorizer(stop_words="english", min_df=1)
MATRIX = TFIDF.fit_transform(CORPUS)

# Build tag → document mapping
TAG_INDEX = {}
i = 0
while i < len(METAINFO):
    for tag in METAINFO[i]["labels"]:
        norm = normalize_tag(tag)
        if norm:
            TAG_INDEX.setdefault(norm, set()).add(i)
    i += 1

UNIQUE_TAGS = sorted(set(normalize_tag(t) for m in METAINFO for t in m["labels"]))

VOCAB_TOKENS = set(TFIDF.get_feature_names_out())


# ------------------------------------------------------------------------------
# Boolean Search Utilities
# ------------------------------------------------------------------------------
def detect_boolean(expr: str) -> bool:
    expanded = " " + expr.upper() + " "
    return (" AND " in expanded) or (" OR " in expanded)


def resolve_boolean(expr: str) -> set:
    pieces = [p.strip() for p in expr.split() if p.strip()]
    if not pieces:
        return set()

    seq = []
    idx = 0
    while idx < len(pieces):
        token = pieces[idx]
        if token.upper() in ("AND", "OR"):
            seq.append(token.upper())
        else:
            cleaned = re.sub(r"[^a-zA-Z]", "", token).lower()
            if cleaned in VOCAB_TOKENS:
                col = TFIDF.vocabulary_.get(cleaned)
                rows, _ = MATRIX[:, col].nonzero()
                seq.append(set(int(x) for x in rows))
            else:
                seq.append(set())
        idx += 1

    # Handle AND first
    k = 0
    while k < len(seq):
        if seq[k] == "AND" and 0 < k < len(seq) - 1:
            A = seq[k - 1]
            B = seq[k + 1]
            if isinstance(A, set) and isinstance(B, set):
                merged = A & B
                seq = seq[:k - 1] + [merged] + seq[k + 2:]
                k -= 1
            else:
                k += 1
        else:
            k += 1

    # Handle OR
    final = set()
    for element in seq:
        if isinstance(element, set):
            final |= element

    return final


# ------------------------------------------------------------------------------
# Flask Application
# ------------------------------------------------------------------------------
app = Flask(__name__, template_folder=TEMPLATE_PATH)


@app.route("/")
def index_page():
    return render_template("index.html")


@app.route("/tags")
def list_tags():
    return jsonify(UNIQUE_TAGS)


@app.route("/query", methods=["POST"])
def handle_query():
    body = request.get_json() or {}

    user_query = (body.get("query") or "").strip()
    raw_filters = body.get("tag_filter") or []

    if not user_query and not raw_filters:
        return jsonify({"error": "Provide a search query or tag filters."}), 400

    try:
        k = int(body.get("top_k", 5))
        if k <= 0:
            raise ValueError
    except Exception:
        return jsonify({"error": "Invalid top_k"}), 400

    cleaned_filters = []
    x = 0
    while x < len(raw_filters):
        if isinstance(raw_filters[x], str):
            t = normalize_tag(raw_filters[x])
            if t:
                cleaned_filters.append(t)
        x += 1

    # Start with all documents
    pool = set(range(len(CORPUS)))

    # Apply tag filters
    if cleaned_filters:
        allowed = set()
        y = 0
        while y < len(cleaned_filters):
            tag = cleaned_filters[y]
            allowed |= TAG_INDEX.get(tag, set())
            y += 1
        pool &= allowed

        if not pool:
            return jsonify([])

    # Boolean mode
    if detect_boolean(user_query):
        matched = resolve_boolean(user_query)
        pool &= matched

        if not pool:
            return jsonify([])

        selected = list(pool)[:k]
        out = []
        z = 0
        while z < len(selected):
            ref = METAINFO[selected[z]]
            out.append({
                "writer": ref["writer"],
                "content": ref["body"],
                "labels": ref["labels"],
                "similarity": None
            })
            z += 1
        return jsonify(out)

    # Semantic mode
    q_vec = TFIDF.transform([user_query])
    sim_scores = cosine_similarity(q_vec, MATRIX)[0]

    ranked_ids = sorted(pool, key=lambda r: sim_scores[r], reverse=True)

    result = []
    idx2 = 0
    while idx2 < len(ranked_ids):
        doc_id = ranked_ids[idx2]
        if sim_scores[doc_id] <= 0:
            break

        m = METAINFO[doc_id]
        result.append({
            "writer": m["writer"],
            "content": m["body"],
            "labels": m["labels"],
            "similarity": round(float(sim_scores[doc_id]), 4)
        })

        if len(result) >= k:
            break

        idx2 += 1

    return jsonify(result)


# ------------------------------------------------------------------------------
# Run Server
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

