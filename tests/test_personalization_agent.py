from agents.personalization_agent import PersonalizationAgent, UserProfile


def test_personalization_agent_creates_default_profile():
    agent = PersonalizationAgent()

    profile = agent.create_default_profile()

    assert profile.role == "student"
    assert profile.technical_level == "beginner"
    assert profile.response_style == "balanced"
    assert profile.preferred_format == "bullet"


def test_personalization_agent_creates_profile():
    agent = PersonalizationAgent()

    profile = agent.create_profile(
        role="analyst",
        technical_level="advanced",
        response_style="detailed",
        preferred_format="step_by_step",
    )

    assert profile.role == "analyst"
    assert profile.technical_level == "advanced"
    assert profile.response_style == "detailed"
    assert profile.preferred_format == "step_by_step"


def test_personalization_agent_fallbacks_invalid_profile_values():
    agent = PersonalizationAgent()

    profile = agent.create_profile(
        role="",
        technical_level="expert",
        response_style="very long",
        preferred_format="table",
    )

    assert profile.role == "student"
    assert profile.technical_level == "beginner"
    assert profile.response_style == "balanced"
    assert profile.preferred_format == "bullet"


def test_personalization_agent_beginner_response():
    agent = PersonalizationAgent()
    profile = UserProfile(
        role="student",
        technical_level="beginner",
        response_style="balanced",
        preferred_format="bullet",
    )

    result = agent.personalize_response(
        content="The dataset contains 10 rows and 3 columns.",
        profile=profile,
    )

    assert "Beginner-friendly explanation" in result.personalized_content
    assert "beginner_explanation" in result.applied_rules


def test_personalization_agent_advanced_response():
    agent = PersonalizationAgent()
    profile = UserProfile(
        role="data analyst",
        technical_level="advanced",
        response_style="balanced",
        preferred_format="bullet",
    )

    result = agent.personalize_response(
        content="The dataset contains 10 rows and 3 columns.",
        profile=profile,
    )

    assert "Technical explanation" in result.personalized_content
    assert "advanced_explanation" in result.applied_rules


def test_personalization_agent_step_by_step_format():
    agent = PersonalizationAgent()
    profile = UserProfile(
        role="student",
        technical_level="beginner",
        response_style="balanced",
        preferred_format="step_by_step",
    )

    result = agent.personalize_response(
        content="The dataset contains 10 rows and 3 columns.",
        profile=profile,
    )

    assert "Step 1" in result.personalized_content
    assert "step_by_step_format" in result.applied_rules


def test_personalization_agent_empty_content_warning():
    agent = PersonalizationAgent()
    profile = agent.create_default_profile()

    result = agent.personalize_response(
        content="",
        profile=profile,
    )

    assert result.warnings
    assert "No content" in result.personalized_content

def test_personalization_agent_concise_style_limits_lines():
    agent = PersonalizationAgent()
    profile = UserProfile(
        role="student",
        technical_level="intermediate",
        response_style="concise",
        preferred_format="bullet",
    )

    content = "\n".join(
        [
            "Line 1",
            "Line 2",
            "Line 3",
            "Line 4",
            "Line 5",
            "Line 6",
            "Line 7",
            "Line 8",
            "Line 9",
        ]
    )

    result = agent.personalize_response(
        content=content,
        profile=profile,
    )

    non_empty_lines = [
        line
        for line in result.personalized_content.splitlines()
        if line.strip()
    ]

    assert len(non_empty_lines) <= 8
    assert "concise_style" in result.applied_rules


def test_personalization_agent_paragraph_format():
    agent = PersonalizationAgent()
    profile = UserProfile(
        role="student",
        technical_level="intermediate",
        response_style="balanced",
        preferred_format="paragraph",
    )

    result = agent.personalize_response(
        content="- First point\n- Second point",
        profile=profile,
    )

    assert "paragraph_format" in result.applied_rules
    assert "\n- " not in result.personalized_content


def test_personalization_agent_summarizes_profile():
    agent = PersonalizationAgent()
    profile = agent.create_profile(
        role="analyst",
        technical_level="advanced",
        response_style="detailed",
        preferred_format="step_by_step",
    )

    summary = agent.summarize_profile(profile)

    assert summary["role"] == "analyst"
    assert summary["technical_level"] == "advanced"
    assert summary["response_style"] == "detailed"
    assert summary["preferred_format"] == "step_by_step"