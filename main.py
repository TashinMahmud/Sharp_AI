from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class GenerateRequest(BaseModel):
    topic: str
    difficulty: str

class ArgumentResponse(BaseModel):
    main_arguments: List[str]
    counter_arguments: List[str]
    rebuttals: List[str]

class QuizRequest(BaseModel):
    topic: str
    difficulty: str
    arguments: List[str]

class QuizResponse(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class HintRequest(BaseModel):
    question: str
    arguments: List[str]

class HintResponse(BaseModel):
    hint: str

class EvaluateRequest(BaseModel):
    question: str
    selected_answer: str
    correct_answer: str
    difficulty: str

class EvaluateResponse(BaseModel):
    feedback: str


def call_ai(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You must respond with valid JSON only. Do not include any extra text."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    return json.loads(response.choices[0].message.content)

@app.post("/generate", response_model=ArgumentResponse)
def generate_arguments(req: GenerateRequest):
    prompt = f"""
Generate arguments for the topic: "{req.topic}"
Difficulty: {req.difficulty}

Return valid JSON only with:
main_arguments: list
counter_arguments: list
rebuttals: list
"""
    return call_ai(prompt)


@app.post("/quiz", response_model=QuizResponse)
def generate_quiz(req: QuizRequest):
    prompt = f"""
Create ONE multiple-choice quiz question from this argument:
"{req.arguments[0]}"

Topic: {req.topic}
Difficulty: {req.difficulty}

Return valid JSON only with:
question
options (4 items)
correct_answer (index)
explanation
"""
    return call_ai(prompt)


@app.post("/hint", response_model=HintResponse)
def generate_hint(req: HintRequest):
    prompt = f"""
Give a helpful hint for this question without revealing the answer.

Question:
"{req.question}"

Context arguments:
{req.arguments}

Return valid JSON only with:
hint
"""
    return call_ai(prompt)


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate_answer(req: EvaluateRequest):
    prompt = f"""
You are a debate coach.

Question:
{req.question}

Student answer:
{req.selected_answer}

Correct answer:
{req.correct_answer}

Difficulty:
{req.difficulty}

Give short, constructive feedback.
Return valid JSON only with:
feedback
"""
    return call_ai(prompt)
