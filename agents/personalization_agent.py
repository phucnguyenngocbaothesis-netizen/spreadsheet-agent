from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class UserProfile:
    role: str
    technical_level: str
    response_style: str
    preferred_format: str


@dataclass
class PersonalizationResult:
    original_content: str
    personalized_content: str
    profile: UserProfile
    applied_rules: list[str]
    warnings: list[str]


class PersonalizationAgent:
    """
    Week 7 v0.1:
    Rule-based response personalization.

    This version does not use an LLM.
    It adapts wording, structure, and explanation depth using a manual user profile.
    """

    TECHNICAL_LEVELS = {"beginner", "intermediate", "advanced"}
    RESPONSE_STYLES = {"concise", "balanced", "detailed"}
    PREFERRED_FORMATS = {"bullet", "paragraph", "step_by_step"}

    def create_default_profile(self) -> UserProfile:
        return UserProfile(
            role="student",
            technical_level="beginner",
            response_style="balanced",
            preferred_format="bullet",
        )

    def create_profile(
        self,
        role: str,
        technical_level: str,
        response_style: str,
        preferred_format: str,
    ) -> UserProfile:
        technical_level = technical_level.lower().strip()
        response_style = response_style.lower().strip()
        preferred_format = preferred_format.lower().strip()

        if technical_level not in self.TECHNICAL_LEVELS:
            technical_level = "beginner"

        if response_style not in self.RESPONSE_STYLES:
            response_style = "balanced"

        if preferred_format not in self.PREFERRED_FORMATS:
            preferred_format = "bullet"

        return UserProfile(
            role=role.strip() or "student",
            technical_level=technical_level,
            response_style=response_style,
            preferred_format=preferred_format,
        )

    def personalize_response(
        self,
        content: str,
        profile: UserProfile,
    ) -> PersonalizationResult:
        applied_rules: list[str] = []
        warnings: list[str] = []

        if not content.strip():
            return PersonalizationResult(
                original_content=content,
                personalized_content="No content was provided for personalization.",
                profile=profile,
                applied_rules=[],
                warnings=["Empty content received."],
            )

        personalized = content.strip()

        personalized = self._adapt_technical_level(
            personalized,
            profile,
            applied_rules,
        )

        personalized = self._adapt_response_style(
            personalized,
            profile,
            applied_rules,
        )

        personalized = self._adapt_format(
            personalized,
            profile,
            applied_rules,
        )

        return PersonalizationResult(
            original_content=content,
            personalized_content=personalized,
            profile=profile,
            applied_rules=applied_rules,
            warnings=warnings,
        )

    def summarize_profile(self, profile: UserProfile) -> dict[str, Any]:
        return {
            "role": profile.role,
            "technical_level": profile.technical_level,
            "response_style": profile.response_style,
            "preferred_format": profile.preferred_format,
        }

    def _adapt_technical_level(
        self,
        content: str,
        profile: UserProfile,
        applied_rules: list[str],
    ) -> str:
        if profile.technical_level == "beginner":
            applied_rules.append("beginner_explanation")
            return (
                "Beginner-friendly explanation:\n\n"
                + content
                + "\n\nIn simple terms, this result helps you understand the dataset without needing advanced statistics."
            )

        if profile.technical_level == "advanced":
            applied_rules.append("advanced_explanation")
            return (
                "Technical explanation:\n\n"
                + content
                + "\n\nThis output should be interpreted as a deterministic result generated from the current dataframe profile."
            )

        applied_rules.append("intermediate_explanation")
        return "Intermediate explanation:\n\n" + content

    def _adapt_response_style(
        self,
        content: str,
        profile: UserProfile,
        applied_rules: list[str],
    ) -> str:
        if profile.response_style == "concise":
            applied_rules.append("concise_style")
            lines = [line for line in content.splitlines() if line.strip()]
            return "\n".join(lines[:8])

        if profile.response_style == "detailed":
            applied_rules.append("detailed_style")
            return (
                content
                + "\n\nAdditional note: Review the evidence and assumptions before making decisions from this output."
            )

        applied_rules.append("balanced_style")
        return content

    def _adapt_format(
        self,
        content: str,
        profile: UserProfile,
        applied_rules: list[str],
    ) -> str:
        if profile.preferred_format == "paragraph":
            applied_rules.append("paragraph_format")
            return content.replace("\n- ", " ").replace("\n", " ")

        if profile.preferred_format == "step_by_step":
            applied_rules.append("step_by_step_format")
            return (
                "Step 1: Read the result.\n"
                "Step 2: Check the evidence or warnings.\n"
                "Step 3: Decide the next action.\n\n"
                + content
            )

        applied_rules.append("bullet_format")
        return content