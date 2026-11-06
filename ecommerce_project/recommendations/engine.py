"""Content-based product recommendations for the SmartFinds catalogue."""
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def recommend_similar_products(products: Iterable, target_product_id: int, limit: int = 3):
    """Return product objects ranked by TF-IDF cosine similarity.

    The source product is excluded. Missing IDs, tiny catalogues and empty text
    are handled without raising errors.
    """
    if limit < 1:
        return []

    items = list(products)
    target_index = next(
        (index for index, item in enumerate(items) if item.id == target_product_id),
        None,
    )
    if target_index is None or len(items) < 2:
        return []

    documents = [
        " ".join(
            part.strip()
            for part in (getattr(item, "name", "") or "", getattr(item, "description", "") or "")
            if part and part.strip()
        )
        for item in items
    ]
    if not any(documents):
        return []

    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(documents)
    except ValueError:
        return []

    scores = cosine_similarity(matrix[target_index], matrix).ravel()
    ranked = sorted(
        (i for i in range(len(items)) if i != target_index and scores[i] > 0),
        key=lambda i: (-float(scores[i]), str(items[i].id)),
    )
    return [items[i] for i in ranked[:limit]]
