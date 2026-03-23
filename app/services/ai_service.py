
import json
import logging
from typing import Any, Optional

from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import get_settings
from app.services.rag_service import build_topic_generation_prompt, build_training_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    @staticmethod
    def get_instance() -> "AIService":
        return AIService()


    @retry(
        retry=retry_if_exception_type((APIConnectionError, RateLimitError, APIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _call_ai(self, prompt: str) -> dict[str, Any]:
        try:
            logger.info(f"Calling OpenAI with model: {self._model}")
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
            result = json.loads(content)
            
            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                # Cost for gpt-4o-mini
                cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.0000006)
                
                result["usage"] = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "totalTokens": total_tokens,
                    "totalPrompts": 1,
                    "estimated_cost_usd": cost,
                    "model": "gpt-4o-mini"
                }

            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from AI response: {e}")
            raise ValueError(f"AI returned invalid JSON: {e}") from e
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            raise

    def generate_arguments(self, topic: str, difficulty: int) -> dict[str, Any]:
        difficulty_str = {1: "very easy", 2: "easy", 3: "medium", 4: "hard", 5: "expert"}.get(difficulty, "medium")
        prompt = f"""
Generate comprehensive study materials for the topic: "{topic}"
Difficulty: {difficulty}/5 ({difficulty_str})

You must generate EXACTLY 5 items for each category. Each item should be a complete, well-reasoned point.

Return valid JSON only with:
{{
  "main_arguments": ["arg1", "arg2", "arg3", "arg4", "arg5"],
  "counter_arguments": ["counter1", "counter2", "counter3", "counter4", "counter5"],
  "rebuttals": ["rebuttal1", "rebuttal2", "rebuttal3", "rebuttal4", "rebuttal5"]
}}
"""
        raw_result = self._call_ai(prompt)
        return {
            "content": {
                "main_arguments": raw_result.get("main_arguments", []),
                "counter_arguments": raw_result.get("counter_arguments", []),
                "rebuttals": raw_result.get("rebuttals", [])
            },
            "generatedBy": "gpt-4o-mini",
            "usage": raw_result.get("usage", {})
        }

    def generate_quiz(
        self, topic: str, difficulty: str, arguments: list[str]
    ) -> dict[str, Any]:
        args_text = "\n".join(f"- {arg}" for arg in arguments)
        prompt = f"""
Create ONE multiple-choice quiz question based on these arguments:
{args_text}

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
        difficulty: int,
    ) -> dict[str, Any]:
        prompt = f"""
You are a debate coach.

Question:
{question}

Student answer:
{selected_answer}

Correct answer:
{correct_answer}

Difficulty:
{difficulty}/5

Give short, constructive feedback and score the answer as a float between 0.0 (wrong) and 1.0 (perfect).
Return valid JSON only with exactly these keys:
"feedback"
"score"
"""
        raw_result = self._call_ai(prompt)
        return {
            "score": float(raw_result.get("score", 0.0)),
            "feedback": raw_result.get("feedback", "No feedback provided."),
            "answer": {"selected_answer": selected_answer, "correct_answer": correct_answer},
            "usage": raw_result.get("usage", {})
        }

    def generate_training(
        self,
        topic: str,
        topic_id: int,
        difficulty: str,
        message: str,
        user_id: int,
        study_materials: Optional[str] = None,
    ) -> dict[str, Any]:
        """Stateless Training Generator based on Difficulty."""

        prompt = build_training_prompt(
            topic=topic,
            topic_id=topic_id,
            user_id=user_id,
            difficulty=difficulty,
            user_message=message,
            study_materials=study_materials
        )

        result = self._call_ai(prompt)

        if "structured_data" in result and "usage" in result:
            result["structured_data"]["usage"] = result.pop("usage")

        return result

    def generate_topic_card(
        self,
        topic: str,
        topic_id: int,
        message: str,
        user_id: int,
        study_materials: Optional[str] = None,
    ) -> dict[str, Any]:
        """Stateless Topic Card generator. Produces the 4-part argument card."""

        prompt = build_topic_generation_prompt(
            topic=topic,
            topic_id=topic_id,
            user_id=user_id,
            user_message=message,
            study_materials=study_materials
        )

        result = self._call_ai(prompt)

        # Inject the real usage metrics into structured_data
        if "structured_data" in result and "usage" in result:
            result["structured_data"]["usage"] = result.pop("usage")

        return result


def get_ai_service() -> AIService:
    return AIService()
