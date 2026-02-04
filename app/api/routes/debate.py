"""Debate/quiz API routes."""

from fastapi import APIRouter, HTTPException, Request
from openai import APIError, APIConnectionError, AuthenticationError, RateLimitError

from app.core.limiter import limiter
from app.schemas import (
    ArgumentResponse,
    DebateChatRequest,
    DebateChatResponse,
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


def _handle_ai_errors(e: Exception) -> HTTPException:
    if isinstance(e, RateLimitError):
        return HTTPException(status_code=429, detail="AI rate limit exceeded. Try again shortly.")
    if isinstance(e, AuthenticationError):
        return HTTPException(status_code=401, detail="Invalid AI API key.")
    if isinstance(e, (APIError, APIConnectionError)):
        return HTTPException(status_code=503, detail="AI service temporarily unavailable. Try again later.")
    return HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=ArgumentResponse)
@limiter.limit("30/minute")
def generate_arguments(request: Request, req: GenerateRequest):
    """Generate main arguments, counter arguments, and rebuttals for a topic."""
    try:
        service = get_ai_service()
        return service.generate_arguments(req.topic, req.difficulty)
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e


@router.post("/quiz", response_model=QuizResponse)
@limiter.limit("30/minute")
def generate_quiz(request: Request, req: QuizRequest):
    """Generate a multiple-choice quiz question from an argument."""
    try:
        service = get_ai_service()
        return service.generate_quiz(
            req.topic, req.difficulty, req.arguments[0]
        )
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e


@router.post("/hint", response_model=HintResponse)
@limiter.limit("30/minute")
def generate_hint(request: Request, req: HintRequest):
    """Generate a helpful hint for a question without revealing the answer."""
    try:
        service = get_ai_service()
        return service.generate_hint(req.question, req.arguments)
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e


@router.post("/evaluate", response_model=EvaluateResponse)
@limiter.limit("30/minute")
def evaluate_answer(request: Request, req: EvaluateRequest):
    """Evaluate a student's answer and provide constructive feedback."""
    try:
        service = get_ai_service()
        return service.evaluate_answer(
            req.question,
            req.selected_answer,
            req.correct_answer,
            req.difficulty,
        )
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e


@router.post("/debate/chat", response_model=DebateChatResponse)
@limiter.limit("30/minute")
def debate_chat(request: Request, req: DebateChatRequest):
    """Single debate-style chat turn based on user role and history."""
    try:
        service = get_ai_service()
        history = (
            [turn.model_dump() for turn in req.debate_history]
            if req.debate_history
            else None
        )
        return service.debate_chat(
            topic=req.topic,
            difficulty=req.difficulty,
            role=req.role,
            message=req.message,
            debate_history=history,
        )
    except (ValueError, RateLimitError, AuthenticationError, APIError, APIConnectionError) as e:
        raise _handle_ai_errors(e) from e
