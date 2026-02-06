
from typing import Optional

def build_debate_prompt(
    topic: str,
    difficulty: str,
    role: str,
    user_message: str,
    history_text: str,
    retrieved_context: str,
    study_materials: Optional[str] = None
) -> str:
    
    context_section = ""
    if retrieved_context:
        context_section += f"\nRelevant Context from Past Sessions:\n{retrieved_context}\n"
    
    if study_materials:
        context_section += f"\nCore Study Materials for this Topic:\n{study_materials}\n"

    prompt = f"""
You are an AI debate coach helping a user practice the topic "{topic}".
Difficulty: {difficulty}

Core arguments the student has studied:
{study_materials if study_materials else "No specific materials loaded."}

The user is sending a new message in the role: {role}.

{context_section}

Current Session History:
{history_text}

Current user message:
{user_message}

Respond with exactly one of the following roles in the JSON field "ai_role":
- "counter_argument" when the user_role is "user_argument"
- "rebuttal" when the user_role is "user_counter"
- "challenge" when the user_role is "user_rebuttal"

Return valid JSON only with:
ai_role
ai_message
"""
    return prompt
