from unittest.mock import MagicMock, patch

from agents.models.interface import Model

from src.github_agents.issue_analyze_agent import (
    IssueAnalysisResponse,
    IssueCategory,
    create_issue_analyze_agent,
)


def test_issue_category_model():
    """Test the IssueCategory model with various confidence values."""
    # Test with valid confidence values
    category1 = IssueCategory(name="bug", confidence=0.8)
    assert category1.name == "bug"
    assert category1.confidence == 0.8

    category2 = IssueCategory(name="feature", confidence=0.0)
    assert category2.name == "feature"
    assert category2.confidence == 0.0

    category3 = IssueCategory(name="question", confidence=1.0)
    assert category3.name == "question"
    assert category3.confidence == 1.0

    # Test with confidence values outside the described range
    # (should still work after removing ge/le constraints)
    category4 = IssueCategory(name="invalid", confidence=1.5)
    assert category4.name == "invalid"
    assert category4.confidence == 1.5

    category5 = IssueCategory(name="negative", confidence=-0.5)
    assert category5.name == "negative"
    assert category5.confidence == -0.5


def test_issue_analysis_response_model():
    """Test that the IssueAnalysisResponse model works with IssueCategory."""
    category = IssueCategory(name="bug", confidence=0.9)

    response = IssueAnalysisResponse(
        summary="Test issue summary",
        category=category,
        complexity="medium",
        priority="high",
        related_areas=["src/module1", "src/module2"],
        next_steps=["Fix the bug", "Add tests"],
    )

    assert response.summary == "Test issue summary"
    assert response.category.name == "bug"
    assert response.category.confidence == 0.9
    assert response.complexity == "medium"
    assert response.priority == "high"
    assert response.related_areas == ["src/module1", "src/module2"]
    assert response.next_steps == ["Fix the bug", "Add tests"]


@patch("src.github_agents.issue_analyze_agent.WebSearchTool")
@patch("src.github_agents.issue_analyze_agent.OpenAIProvider")
def test_create_issue_analyze_agent(mock_provider, mock_web_search_tool):
    """Test that the agent creation function works with the default model."""
    mock_model = MagicMock(spec=Model)
    mock_provider.return_value.get_model.return_value = mock_model
    agent = create_issue_analyze_agent()
    assert agent.name == "Issue Analysis Agent"
    assert agent.model == mock_model
    assert agent.output_type == IssueAnalysisResponse
    assert len(agent.tools) == 11
    assert mock_web_search_tool.return_value in agent.tools

    # Test with custom model and prompt
    custom_model_name = "gpt-4o"
    custom_prompt = "Custom prompt for testing"

    agent = create_issue_analyze_agent(model=custom_model_name, custom_prompt=custom_prompt)
    assert agent.name == "Issue Analysis Agent"
    assert agent.model == mock_model
    assert agent.output_type == IssueAnalysisResponse
