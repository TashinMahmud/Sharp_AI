"""Debate/quiz API routes."""

from fastapi import APIRouter, HTTPException

from app.schemas import (
    ArgumentResponse,
    EvaluateRequest,
    EvaluateResponse,
    GenerateRequest,
    HintRequest,
    HintResponse,
    QuizRequest,
    QuizResponse,
)
from app.services.ai_service import get_ai_service

router = APIRouter(tags=["debate"])


@router.post("/generate", response_model=ArgumentResponse)
def generate_arguments(req: GenerateRequest):
    """Generate main arguments, counter arguments, and rebuttals for a topic."""
    try:
        service = get_ai_service()
        return service.generate_arguments(req.topic, req.difficulty)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/quiz", response_model=QuizResponse)
def generate_quiz(req: QuizRequest):
    """Generate a multiple-choice quiz question from an argument."""
    if not req.arguments:
        raise HTTPException(
            status_code=422, detail="At least one argument is required"
        )
    try:
        service = get_ai_service()
        return service.generate_quiz(
            req.topic, req.difficulty, req.arguments[0]
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/hint", response_model=HintResponse)
def generate_hint(req: HintRequest):
    """Generate a helpful hint for a question without revealing the answer."""
    try:
        service = get_ai_service()
        return service.generate_hint(req.question, req.arguments)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_answer(req: EvaluateRequest):
    """Evaluate a student's answer and provide constructive feedback."""
    try:
        service = get_ai_service()
        return service.evaluate_answer(
            req.question,
            req.selected_answer,
            req.correct_answer,
            req.difficulty,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
