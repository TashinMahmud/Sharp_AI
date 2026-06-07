
import json
import logging
from typing import Any, Optional

from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import get_settings
from app.services.rag_service import build_topic_generation_prompt, build_training_prompt, build_hint_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:

    def __init__(self) -> None:
        settings = get_settings()
        if settings.groq_api_key:
            self._client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
            self._model = settings.groq_model
            self._provider = "Groq"
        else:
            if not settings.openai_api_key:
                raise ValueError("Either OPENAI_API_KEY or GROQ_API_KEY must be set in environment")
            self._client = OpenAI(api_key=settings.openai_api_key)
            self._model = settings.openai_model
            self._provider = "OpenAI"

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
            logger.info(f"Calling {self._provider} with model: {self._model}")
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
                
                # Calculate cost only for OpenAI gpt-4o-mini, set to 0 for Groq
                cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.0000006) if self._provider == "OpenAI" else 0.0
                
                result["usage"] = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "totalTokens": total_tokens,
                    "totalPrompts": 1,
                    "estimated_cost_usd": cost,
                    "model": self._model
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

    def generate_hint(
        self,
        category: str,
        title: str,
        materials: str,
        user_message: str,
        difficulty: str
    ) -> dict[str, Any]:
        prompt = build_hint_prompt(
            category=category,
            title=title,
            materials=materials,
            user_message=user_message,
            difficulty=difficulty
        )
        result = self._call_ai(prompt)
        
        if "usage" in result:
            result["structured_data"] = {"usage": result.pop("usage")}
        else:
            result["structured_data"] = {}
            
        return result

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
        category: str,
        title: str,
        materials: str,
        message: str,
        difficulty: str
    ) -> dict[str, Any]:
        """Stateless Training Generator based on Difficulty."""
        prompt = build_training_prompt(
            category=category,
            title=title,
            materials=materials,
            user_message=message,
            difficulty=difficulty
        )
        result = self._call_ai(prompt)

        if "usage" in result:
            result["structured_data"] = {"usage": result.pop("usage")}
        else:
            result["structured_data"] = {}
            
        result["category"] = category
        result["title"] = title
        result["difficulty"] = difficulty
        result["score"] = float(result.get("score", 0.0))
        result["evaluation"] = str(result.get("evaluation", ""))

        return result

    def generate_topic_card(
        self,
        category: str,
        message: str
    ) -> dict[str, Any]:
        """Stateless Topic Card generator. Produces the 4-part argument card."""
        prompt = build_topic_generation_prompt(
            category=category,
            user_message=message
        )
        result = self._call_ai(prompt)

        if "usage" in result:
            result["structured_data"] = {"usage": result.pop("usage")}
        else:
            result["structured_data"] = {}

        return result


def get_ai_service() -> AIService:
    return AIService()
