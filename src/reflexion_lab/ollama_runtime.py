from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import requests
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from .schemas import QAExample, JudgeResult, ReflectionEntry
from .utils import normalize_answer


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"
REQUEST_TIMEOUT = 120


@dataclass
class LLMResponse:
    text: str
    total_tokens: int
    latency_ms: int


def _extract_total_tokens(data: dict[str, Any]) -> int:
    
    prompt_eval_count = data.get("prompt_eval_count", 0) or 0
    eval_count = data.get("eval_count", 0) or 0
    return int(prompt_eval_count) + int(eval_count)


def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> LLMResponse:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
        },
    }

    start = time.perf_counter()
    response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    end = time.perf_counter()

    text = (data.get("response") or "").strip()
    total_tokens = _extract_total_tokens(data)
    latency_ms = int((end - start) * 1000)

    return LLMResponse(text=text, total_tokens=total_tokens, latency_ms=latency_ms)


def build_actor_prompt(
    example: QAExample,
    attempt_id: int,
    agent_type: str,
    reflection_memory: list[str],
) -> str:
    reflection_text = "\n".join(f"- {item}" for item in reflection_memory) if reflection_memory else "None"
    context_text = "\n".join(
        f"Title: {chunk.title}\nText: {chunk.text}"
        for chunk in example.context
    )

    return f"""
{ACTOR_SYSTEM}

Question:
{example.question}

Context:
{context_text}

Reflection memory:
{reflection_text}

Attempt: {attempt_id}
Agent type: {agent_type}
""".strip()




def build_evaluator_prompt(example: QAExample, answer: str) -> str:
    return f"""
{EVALUATOR_SYSTEM}

Question: {example.question}
Gold answer: {example.gold_answer}
Predicted answer: {answer}
""".strip()


def build_reflector_prompt(example: QAExample, answer: str, judge: JudgeResult) -> str:
    missing_evidence = judge.missing_evidence or []
    spurious_claims = judge.spurious_claims or []

    return f"""
{REFLECTOR_SYSTEM}

Question: {example.question}
Gold answer: {example.gold_answer}
Wrong answer: {answer}
Judge reason: {judge.reason}
Missing evidence: {missing_evidence}
Spurious claims: {spurious_claims}
""".strip()


def _safe_json_loads(text: str) -> dict[str, Any]:
    """
    Cố parse JSON. Nếu model lỡ bày trò bọc markdown hoặc nói linh tinh,
    ta cố cứu trước khi bỏ cuộc. Vì model nào cũng thích phá format lúc rảnh.
    """
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        lines = [line for line in lines if not line.strip().startswith("```")]
        text = "\n".join(lines).strip()

    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]

    return json.loads(text)


def actor_answer(
    example: QAExample,
    attempt_id: int,
    agent_type: str,
    reflection_memory: list[str],
) -> tuple[str, int, int]:
    prompt = build_actor_prompt(example, attempt_id, agent_type, reflection_memory)
    llm_result = call_ollama(prompt)
    answer = llm_result.text.strip()

    if answer.lower().startswith("answer:"):
        answer = answer.split(":", 1)[1].strip()

    return answer, llm_result.total_tokens, llm_result.latency_ms


def evaluator(example: QAExample, answer: str) -> tuple[JudgeResult, int, int]:
    """
    Ưu tiên dùng exact/normalized match để giữ benchmark ổn định.
    Nếu sai thì mới gọi LLM evaluator để giải thích lỗi.
    """
    if normalize_answer(example.gold_answer) == normalize_answer(answer):
        judge = JudgeResult(
            score=1,
            reason="Final answer matches the gold answer after normalization.",
            missing_evidence=[],
            spurious_claims=[],
        )
        return judge, 0, 0

    prompt = build_evaluator_prompt(example, answer)
    llm_result = call_ollama(prompt)

    try:
        data = _safe_json_loads(llm_result.text)
        judge = JudgeResult(
            score=int(data.get("score", 0)),
            reason=str(data.get("reason", "Incorrect answer.")),
            missing_evidence=list(data.get("missing_evidence", [])),
            spurious_claims=list(data.get("spurious_claims", [])),
        )
    except Exception:
        judge = JudgeResult(
            score=0,
            reason=f"Evaluator could not parse structured output. Raw output: {llm_result.text[:200]}",
            missing_evidence=["Need to verify all reasoning hops against the source facts."],
            spurious_claims=[answer] if answer else [],
        )

    return judge, llm_result.total_tokens, llm_result.latency_ms


def reflector(example: QAExample, attempt_id: int, answer: str, judge: JudgeResult) -> tuple[ReflectionEntry, int, int]:
    prompt = build_reflector_prompt(example, answer, judge)
    llm_result = call_ollama(prompt)

    try:
        data = _safe_json_loads(llm_result.text)
        lesson = str(data.get("lesson", "The previous attempt missed required evidence."))
        next_strategy = str(data.get("next_strategy", "Verify each reasoning hop before answering."))
    except Exception:
        lesson = "The previous attempt missed or distorted one of the required reasoning hops."
        next_strategy = "Check every hop explicitly and verify the final entity before answering."

    reflection = ReflectionEntry(
        attempt_id=attempt_id,
        failure_reason=judge.reason,
        lesson=lesson,
        next_strategy=next_strategy,
    )

    return reflection, llm_result.total_tokens, llm_result.latency_ms