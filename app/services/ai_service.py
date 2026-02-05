
import json
import logging
from typing import Any, Literal, Optional

from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from langchain_core.messages import HumanMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import get_settings
from app.services.memory_service import MemoryService
from app.services.rag_service import build_debate_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model
        
        self._memory_service = MemoryService.get_instance()

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
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from AI response: {e}")
            raise ValueError(f"AI returned invalid JSON: {e}") from e
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            raise

    def generate_arguments(self, topic: str, difficulty: str) -> dict[str, Any]:
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
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        
        history_text = ""
        memory = None
        if user_id and session_id:
            memory = self._memory_service.get_or_create_memory(user_id, session_id)
            messages = memory.load_memory_variables({}).get("chat_history", [])
            history_text = "\n".join([f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}" for m in messages])

        retrieved_context = ""
        if user_id and session_id:
            retrieved_context = self._memory_service.retrieve_context(user_id, session_id, message)

        prompt = build_debate_prompt(
            topic=topic,
            difficulty=difficulty,
            role=role,
            user_message=message,
            history_text=history_text,
            retrieved_context=retrieved_context
        )

        result = self._call_ai(prompt)
        ai_message = result.get("ai_message", "")
        
        if user_id and session_id and memory:
            self._memory_service.save_turn(user_id, session_id, message, ai_message)
            self._memory_service.save_turn_persistent(user_id, session_id, message, ai_message)
            
            settings = get_settings()
            messages = memory.chat_memory.messages
            if len(messages) >= settings.memory_summary_trigger:
                summary = self.summarize_conversation(messages)
                self._memory_service.summarize_and_store(user_id, session_id, summary)
                
                keep_count = settings.memory_keep_last * 2
                memory.chat_memory.messages = messages[-keep_count:]

        return result

    def summarize_conversation(self, messages: list) -> str:
        if not messages:
            return ""
            
        serialized = "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}" for m in messages
        )
        prompt = f"""Summarize this debate conversation in 2-4 short sentences. Preserve key arguments and positions only.

Conversation:
{serialized}

Return valid JSON only with:
summary
"""
        out = self._call_ai(prompt)
        return out.get("summary", "")


def get_ai_service() -> AIService:
    return AIService()
