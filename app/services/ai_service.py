"""AI service for OpenAI interactions."""

import json
from typing import Any, Literal, Optional

from openai import OpenAI

from app.core.config import get_settings


class AIService:
    """Service for generating content via OpenAI API."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    def _call_ai(self, prompt: str) -> dict[str, Any]:
        """Call OpenAI API and return parsed JSON response."""
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "You must respond with valid JSON only. Do not include any extra text.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI returned invalid JSON: {e}") from e

    def generate_arguments(self, topic: str, difficulty: str) -> dict[str, Any]:
        """Generate main arguments, counter arguments, and rebuttals."""
        prompt = f"""
Generate arguments for the topic: "{topic}"
Difficulty: {difficulty}

Return valid JSON only with:
main_arguments: list
counter_arguments: list
rebuttals: list
"""
        return self._call_ai(prompt)

    def generate_quiz(
        self, topic: str, difficulty: str, argument: str
    ) -> dict[str, Any]:
        """Generate a single multiple-choice quiz question."""
        prompt = f"""
Create ONE multiple-choice quiz question from this argument:
"{argument}"

Topic: {topic}
Difficulty: {difficulty}

Return valid JSON only with:
question
options (4 items)
correct_answer (index)
explanation
"""
        return self._call_ai(prompt)

    def generate_hint(self, question: str, arguments: list[str]) -> dict[str, Any]:
        """Generate a helpful hint without revealing the answer."""
        prompt = f"""
Give a helpful hint for this question without revealing the answer.

Question:
"{question}"

Context arguments:
{arguments}

Return valid JSON only with:
hint
"""
        return self._call_ai(prompt)

    def evaluate_answer(
        self,
        question: str,
        selected_answer: str,
        correct_answer: str,
        difficulty: str,
    ) -> dict[str, Any]:
        """Evaluate a student's answer and provide feedback."""
        prompt = f"""
You are a debate coach.

Question:
{question}

Student answer:
{selected_answer}

Correct answer:
{correct_answer}

Difficulty:
{difficulty}

Give short, constructive feedback.
Return valid JSON only with:
feedback
"""
        return self._call_ai(prompt)

    def debate_chat(
        self,
        topic: str,
        difficulty: str,
        role: Literal["user_argument", "user_counter", "user_rebuttal"],
        message: str,
        debate_history: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """Handle a single debate-style chat turn."""
        history_text = ""
        if debate_history:
            serialized_turns = [
                f"{turn.get('role', 'unknown')}: {turn.get('message', '')}"
                for turn in debate_history
            ]
            history_text = "\nPrevious turns:\n" + "\n".join(serialized_turns)

        prompt = f"""
You are an AI debate partner helping a user practice structured argumentation on the topic "{topic}".
Difficulty: {difficulty}

The user is sending a new message in the role: {role}.
{history_text}

Current user message:
{message}

Respond with exactly one of the following roles in the JSON field "ai_role":
- "counter_argument" when the user_role is "user_argument"
- "rebuttal" when the user_role is "user_counter"
- "challenge" when the user_role is "user_rebuttal"

Return valid JSON only with:
ai_role
ai_message
"""
        return self._call_ai(prompt)


def get_ai_service() -> AIService:
    """Dependency that provides an AIService instance."""
    return AIService()
