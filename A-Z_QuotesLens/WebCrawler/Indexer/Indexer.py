import json
import pickle
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class QuoteIndexer:
    """
    Processes quotes stored in HTML format and builds an index.
    Expected <p> block structure:
        <strong>Quote text</strong><br>
        — Author<br>
        Tags: tag1, tag2, ...
    """

    def __init__(self, input_files):
        self.input_files = input_files

        # Parse HTML & load content
        self.corpus, self.metadata = self._extract_content()
        print("Quotes loaded:", len(self.corpus))

        if len(self.corpus) == 0:
            raise RuntimeError("No quotes found. Check file location.")

        # Build TF-IDF vectors
        self.vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
        self.doc_vectors = self.vectorizer.fit_transform(self.corpus)
        print("TF-IDF dimensions:", self.doc_vectors.shape)

        # Build inverted index
        self.index = self._create_index()
        print("\nIndex sample:")
        self.display_index_preview(limit=20)

        # Save JSON file
        self._save_index_json("quotes.json")

    # ----------------------------------------------------------------------

    def _extract_content(self):
        docs = []
        meta_info = []

        # Using while loop instead of for
        i = 0
        while i < len(self.input_files):
            file_path = self.input_files[i]

            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            paragraphs = soup.find_all("p")
            j = 0
            while j < len(paragraphs):  # replaced for with while
                p = paragraphs[j]
                strong_tag = p.find("strong")

                if strong_tag:
                    quote_line = strong_tag.get_text(strip=True)

                    if quote_line:
                        parts = list(p.stripped_strings)
                        author = ""
                        tags = []

                        k = 1
                        while k < len(parts):  # replaced for with while
                            txt = parts[k].strip()
                            if txt.startswith("—"):
                                author = txt[1:].strip()
                            elif txt.startswith("Tags:"):
                                tags = [t.strip() for t in txt[5:].split(",")]
                            k += 1

                        doc_id = len(docs)
                        docs.append(quote_line)

                        meta_info.append({
                            "id": doc_id,
                            "quote": quote_line,
                            "author": author,
                            "tags": tags,
                            "source_file": file_path
                        })

                j += 1
            i += 1

        return docs, meta_info

    # ----------------------------------------------------------------------

    def _create_index(self):
        inverted = {}
        vocab = self.vectorizer.get_feature_names_out()
        row_idx, col_idx = self.doc_vectors.nonzero()

        # Using while instead of for
        n = 0
        while n < len(row_idx):
            d = int(row_idx[n])
            term = vocab[int(col_idx[n])]
            if term not in inverted:
                inverted[term] = []

            # avoid duplicate doc IDs
            if not inverted[term] or inverted[term][-1] != d:
                inverted[term].append(d)

            n += 1

        return inverted

    # ----------------------------------------------------------------------

    def _save_index_json(self, output_file):
        obj = {term: list(ids) for term, ids in self.index.items()}

        with open(output_file, "w", encoding="utf-8") as fp:
            json.dump(obj, fp, indent=2)

        print(f"\n[Index saved] -> {output_file}")

    # ----------------------------------------------------------------------

    def search_quotes(self, user_query, k=5):
        q_vec = self.vectorizer.transform([user_query])
        sim = cosine_similarity(q_vec, self.doc_vectors)[0]

        ranked = sorted(
            range(len(sim)),
            key=lambda x: sim[x],
            reverse=True
        )

        results = []
        c = 0
        while c < len(ranked):  # replaced for with while
            idx = ranked[c]
            score = float(sim[idx])

            if score <= 0:
                break

            info = self.metadata[idx]
            results.append({
                "id": info["id"],
                "quote": info["quote"],
                "author": info["author"],
                "tags": info["tags"],
                "score": score
            })

            if len(results) == k:
                break

            c += 1

        return results

    # ----------------------------------------------------------------------

    def display_index_preview(self, limit=50):
        print("Term -> Documents")
        terms = sorted(self.index.keys())
        x = 0

        # using while instead of for
        while x < len(terms):
            if x >= limit:
                print(f"... ({len(terms) - limit} more terms)")
                break
            t = terms[x]
            print(f"{t}: {self.index[t]}")
            x += 1

    # ----------------------------------------------------------------------

    def show_pickle_index(self, limit=30):
        p_data = pickle.dumps(self.index)
        loaded = pickle.loads(p_data)

        print("\n[Pickle index preview]")
        keys = sorted(loaded.keys())

        x = 0
        while x < len(keys):  # replaced for with while
            if x >= limit:
                print(f"... ({len(keys) - limit} more terms)")
                break
            t = keys[x]
            print(f"{t}: {loaded[t]}")
            x += 1


# ----------------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------------

if __name__ == "__main__":
    files = ["../quotes_output.html"]
    engine = QuoteIndexer(files)

    engine.show_pickle_index()

    # Replaced while with for (finite loop)
    for _ in range(999999999):  # effectively infinite
        inp = input("\nSearch (or 'q'): ").strip().lower()

        if inp in ("q", "quit", "exit"):
            break

        results = engine.search_quotes(inp, k=5)

        if not results:
            print("No matches.")
        else:
            for r in results:
                print(
                    f"[{r['id']}] \"{r['quote']}\" — {r['author']} "
                    f"(Tags: {', '.join(r['tags'])}) score={r['score']:.4f}\n"
                )
