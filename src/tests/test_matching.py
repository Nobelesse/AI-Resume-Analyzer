from src.matching.keyword_matcher import (
    KeywordMatchResult,
    match_keywords,
    match_skills,
    normalize_term,
    normalize_terms,
)
from src.matching.semantic_matcher import (
    SemanticMatchResult,
    calculate_similarity,
    compare_texts,
)
from src.matching.score_calculator import (
    MatchScoreResult,
    calculate_education_score,
    calculate_experience_score,
    calculate_match_score,
    calculate_project_score,
    calculate_skill_score,
)


class FakeEmbeddingModel:
    """Small deterministic model used for semantic matching tests."""

    def encode(self, texts, convert_to_numpy=True):
        embeddings = []

        for text in texts:
            normalized = text.lower()

            if "python" in normalized:
                embeddings.append([1.0, 0.0, 0.0])
            elif "java" in normalized:
                embeddings.append([0.0, 1.0, 0.0])
            else:
                embeddings.append([0.0, 0.0, 1.0])

        return embeddings


def test_normalize_term():
    assert normalize_term("  Python  ") == "python"
    assert normalize_term("REST APIs") == "REST API"
    assert normalize_term("Postgres") == "PostgreSQL"
    assert normalize_term("") == ""


def test_normalize_terms_removes_duplicates():
    result = normalize_terms(
        [
            "Python",
            "python",
            " SQL ",
            "SQL",
            "REST APIs",
        ]
    )

    assert result == ["python", "sql", "REST API"]


def test_keyword_matching():
    result = match_keywords(
        resume_keywords=[
            "Python",
            "SQL",
            "Pandas",
            "Machine Learning",
        ],
        job_keywords=[
            "Python",
            "SQL",
            "Machine Learning",
            "Docker",
            "AWS",
        ],
    )

    assert isinstance(result, KeywordMatchResult)
    assert result.total_required == 5
    assert result.total_matched == 3
    assert result.match_percentage == 60.0

    assert "python" in [item.lower() for item in result.matched_items]
    assert "SQL" in result.matched_items
    assert "Machine Learning" in result.matched_items

    assert "Docker" in result.missing_items
    assert "AWS" in result.missing_items

    assert "Pandas" in result.extra_items


def test_skill_alias_matching():
    result = match_skills(
        resume_skills=[
            "Python",
            "REST API",
            "PostgreSQL",
        ],
        job_skills=[
            "Python",
            "REST APIs",
            "Postgres",
        ],
    )

    assert result.total_required == 3
    assert result.total_matched == 3
    assert result.match_percentage == 100.0
    assert result.missing_items == []


def test_empty_job_keywords():
    result = match_keywords(
        resume_keywords=["Python", "SQL"],
        job_keywords=[],
    )

    assert result.total_required == 0
    assert result.total_matched == 0
    assert result.match_percentage == 0.0
    assert result.matched_items == []
    assert result.missing_items == []
    assert result.extra_items == ["Python", "SQL"]


def test_empty_resume_keywords():
    result = match_keywords(
        resume_keywords=[],
        job_keywords=["Python", "SQL"],
    )

    assert result.total_required == 2
    assert result.total_matched == 0
    assert result.match_percentage == 0.0
    assert result.matched_items == []
    assert result.missing_items == ["Python", "SQL"]


def test_none_inputs():
    result = match_keywords(
        resume_keywords=None,
        job_keywords=None,
    )

    assert result.total_required == 0
    assert result.total_matched == 0
    assert result.match_percentage == 0.0
    assert result.matched_items == []
    assert result.missing_items == []
    assert result.extra_items == []


def test_semantic_similarity_identical_direction():
    model = FakeEmbeddingModel()

    similarity = calculate_similarity(
        "Python developer",
        "Python programmer",
        model=model,
    )

    assert similarity == 1.0


def test_semantic_similarity_different_content():
    model = FakeEmbeddingModel()

    similarity = calculate_similarity(
        "Python developer",
        "Java developer",
        model=model,
    )

    assert similarity == 0.0


def test_semantic_similarity_empty_text():
    model = FakeEmbeddingModel()

    similarity = calculate_similarity(
        "",
        "Python developer",
        model=model,
    )

    assert similarity == 0.0


def test_compare_texts_success():
    model = FakeEmbeddingModel()

    result = compare_texts(
        resume_text="Python developer",
        job_description="Python programmer",
        model=model,
    )

    assert isinstance(result, SemanticMatchResult)
    assert result.success is True
    assert result.similarity_score == 1.0
    assert result.similarity_percentage == 100.0


def test_compare_texts_empty_input():
    model = FakeEmbeddingModel()

    result = compare_texts(
        resume_text="",
        job_description="Python programmer",
        model=model,
    )

    assert isinstance(result, SemanticMatchResult)
    assert result.success is False
    assert result.similarity_score == 0.0
    assert result.similarity_percentage == 0.0
    assert "required" in result.message.lower()


# ------------------------------------------------------------------
# SCORE CALCULATOR TESTS
# ------------------------------------------------------------------

def test_skill_score():
    score = calculate_skill_score(
        resume_skills=[
            "Python",
            "SQL",
            "Pandas",
        ],
        job_skills=[
            "Python",
            "SQL",
            "Docker",
        ],
    )

    assert score == 66.67


def test_experience_score_full_match():
    score = calculate_experience_score(
        resume_years=3,
        job_requirements=[
            "3 years of experience",
        ],
    )

    assert score == 100.0


def test_experience_score_partial_match():
    score = calculate_experience_score(
        resume_years=1,
        job_requirements=[
            "4 years of experience",
        ],
    )

    assert score == 25.0


def test_experience_score_no_requirement():
    score = calculate_experience_score(
        resume_years=0,
        job_requirements=[],
    )

    assert score == 100.0


def test_education_score():
    score = calculate_education_score(
        resume_education=[
            "Bachelor of Technology in Computer Science",
        ],
        job_education=[
            "Bachelor of Technology in Computer Science",
        ],
    )

    assert score == 100.0


def test_education_score_missing():
    score = calculate_education_score(
        resume_education=[],
        job_education=[
            "Bachelor of Technology in Computer Science",
        ],
    )

    assert score == 0.0


def test_project_score():
    score = calculate_project_score(
        resume_project_text=(
            "Built a Python machine learning project "
            "using Pandas."
        ),
        job_keywords=[
            "Python",
            "Machine Learning",
            "Docker",
        ],
    )

    assert score == 66.67


def test_project_score_no_requirements():
    score = calculate_project_score(
        resume_project_text="Python project",
        job_keywords=[],
    )

    assert score == 100.0


def test_match_score_result_structure():
    """
    Verify the final result structure without loading a real
    Sentence Transformer model.
    """
    result = MatchScoreResult(
        final_score=80.0,
        skills_score=90.0,
        experience_score=80.0,
        education_score=100.0,
        projects_score=70.0,
        semantic_score=75.0,
        skills_weighted_score=36.0,
        experience_weighted_score=20.0,
        education_weighted_score=10.0,
        projects_weighted_score=7.0,
        semantic_weighted_score=11.25,
        semantic_result=SemanticMatchResult(
            similarity_score=0.5,
            similarity_percentage=75.0,
            model_name="test-model",
            success=True,
            message="Test result.",
        ),
        success=True,
        message="Test result.",
    )

    assert result.final_score == 80.0
    assert result.skills_score == 90.0
    assert result.semantic_score == 75.0
    assert result.success is True


def test_score_weights_total_100_percent():
    from src.matching.score_calculator import (
        EDUCATION_WEIGHT,
        EXPERIENCE_WEIGHT,
        PROJECTS_WEIGHT,
        SEMANTIC_WEIGHT,
        SKILLS_WEIGHT,
    )

    total = (
        SKILLS_WEIGHT
        + EXPERIENCE_WEIGHT
        + EDUCATION_WEIGHT
        + PROJECTS_WEIGHT
        + SEMANTIC_WEIGHT
    )

    assert total == 1.0