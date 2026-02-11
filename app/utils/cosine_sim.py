from typing import List

import numpy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt

okt = Okt()
vectorizer = TfidfVectorizer(
    tokenizer=okt.morphs,
    token_pattern=None,)


def calculate_cosine_sim(
    documents: List[str],
    query: str = ""
)-> numpy.ndarray:

    tfidf_matrix = vectorizer.fit_transform(documents + [query])
    cos_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    return cos_sim