"""
Semantic Matching Engine
------------------------

Provides semantic similarity matching between resume text and job
description text using Sentence Transformers.

This module is intentionally independent from Streamlit so it can be
used by the application, tests, or future APIs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Sequence

from sentence_transformers import SentenceTransformer


DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


@dataclass
class SemanticMatchResult:
    """Structured result returned by the semantic matching engine."""

    similarity_score: float
    similarity_percentage: float
    model_name: str
    success: bool
    message: str = ""


@lru_cache(maxsize=2)
def load_embedding_model(
    model_name: str = DEFAULT_MODEL_NAME,
) -> SentenceTransformer:
    """Load and cache the Sentence Transformer model."""
    return SentenceTransformer(model_name)


def _clean_text(text: str | None) -> str:
    """Normalize whitespace in text."""
    if not isinstance(text, str):
        return ""

    return " ".join(text.split())


def _cosine_similarity(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Embedding vectors must have the same dimensions."
        )

    dot_product = sum(
        float(a) * float(b)
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(float(value) ** 2 for value in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(float(value) ** 2 for value in vector_b)
    )

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def _to_vector(embedding: Any) -> Sequence[float]:
    """Convert a model embedding into a simple numeric sequence."""
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()

    if (
        isinstance(embedding, list)
        and embedding
        and isinstance(embedding[0], (list, tuple))
    ):
        embedding = embedding[0]

    if not isinstance(embedding, (list, tuple)):
        raise ValueError(
            "Invalid embedding format returned by the model."
        )

    return embedding


def calculate_similarity(
    text_a: str | None,
    text_b: str | None,
    model: SentenceTransformer | None = None,
) -> float:
    """
    Calculate cosine similarity between two pieces of text.

    Returns a value between -1 and 1 mathematically. For typical
    Sentence Transformer text embeddings, semantically related text
    generally produces positive similarity values.
    """
    clean_a = _clean_text(text_a)
    clean_b = _clean_text(text_b)

    if not clean_a or not clean_b:
        return 0.0

    if model is None:
        model = load_embedding_model()

    embeddings = model.encode(
        [clean_a, clean_b],
        convert_to_numpy=True,
    )

    vector_a = _to_vector(embeddings[0])
    vector_b = _to_vector(embeddings[1])

    similarity = _cosine_similarity(
        vector_a,
        vector_b,
    )

    return max(-1.0, min(1.0, float(similarity)))


def compare_texts(
    resume_text: str | None,
    job_description: str | None,
    model: SentenceTransformer | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> SemanticMatchResult:
    """Compare resume text with a job description."""
    clean_resume = _clean_text(resume_text)
    clean_job = _clean_text(job_description)

    if not clean_resume or not clean_job:
        return SemanticMatchResult(
            similarity_score=0.0,
            similarity_percentage=0.0,
            model_name=model_name,
            success=False,
            message=(
                "Both resume text and job description "
                "are required."
            ),
        )

    try:
        similarity = calculate_similarity(
            text_a=clean_resume,
            text_b=clean_job,
            model=model,
        )

        # Sentence Transformer cosine similarity is converted into
        # a practical matching percentage.
        #
        # Negative cosine values are treated as zero because this
        # application uses the value as a semantic match score.
        percentage = max(0.0, min(1.0, similarity)) * 100.0

        return SemanticMatchResult(
            similarity_score=round(similarity, 4),
            similarity_percentage=round(percentage, 2),
            model_name=model_name,
            success=True,
            message="Semantic comparison completed successfully.",
        )

    except Exception as exc:
        return SemanticMatchResult(
            similarity_score=0.0,
            similarity_percentage=0.0,
            model_name=model_name,
            success=False,
            message=f"Semantic comparison failed: {exc}",
        )