"""Tests for vector similarity helpers used during RAG retrieval."""

from app.shared.rag.vector_store import _cosine_similarity, _embedding_as_list


def test_embedding_as_list_accepts_python_list():
    assert _embedding_as_list([0.1, 0.2, 0.3]) == [0.1, 0.2, 0.3]


def test_embedding_as_list_accepts_tuple():
    assert _embedding_as_list((0.5, 0.5)) == [0.5, 0.5]


def test_embedding_as_list_rejects_invalid_values():
    assert _embedding_as_list(None) is None
    assert _embedding_as_list("not-a-vector") is None


def test_cosine_similarity_for_identical_vectors():
    vector = [1.0, 0.0, 0.0]
    assert _cosine_similarity(vector, vector) == 1.0
