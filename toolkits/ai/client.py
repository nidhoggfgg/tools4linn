from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence

from openai import OpenAI


ReasoningCallback = Callable[[str], None]
AnswerCallback = Callable[[str], None]


def _coerce_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        fragments: List[str] = []
        for item in content:
            if isinstance(item, dict):
                fragments.append(item.get("text", ""))
        return "".join(fragments)
    return str(content)


@dataclass
class ChatResult:
    model: str
    reasoning: str = ""
    answer: str = ""
    usage: Optional[Any] = None
    finish_reason: Optional[str] = None


class AIChatClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
    ) -> None:
        if not api_key:
            raise ValueError("api_key 是必填参数，不能为空")
        if not base_url:
            raise ValueError("base_url 是必填参数，不能为空")

        self._api_key = api_key
        self._base_url = base_url
        self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)

    def chat(
        self,
        messages: Sequence[Dict[str, Any]],
        *,
        model: str,
        stream: bool = True,
        enable_thinking: bool = False,
        thinking_budget: Optional[int] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        on_reasoning: Optional[ReasoningCallback] = None,
        on_answer: Optional[AnswerCallback] = None,
        **request_kwargs: Any,
    ) -> ChatResult:
        payload = dict(extra_body or {})
        if enable_thinking:
            payload.setdefault("enable_thinking", True)
            if thinking_budget is not None:
                payload.setdefault("thinking_budget", thinking_budget)

        request_params: Dict[str, Any] = {
            "model": model,
            "messages": list(messages),
            "stream": stream,
            **request_kwargs,
        }
        if payload:
            request_params["extra_body"] = payload

        completion = self._client.chat.completions.create(**request_params)
        result = ChatResult(model=model)

        if stream:
            for chunk in completion:
                if not chunk.choices:
                    result.usage = getattr(chunk, "usage", None)
                    continue

                choice = chunk.choices[0]
                if choice.finish_reason:
                    result.finish_reason = choice.finish_reason

                delta = choice.delta
                reasoning_piece = getattr(delta, "reasoning_content", None)
                if reasoning_piece:
                    result.reasoning += reasoning_piece
                    if on_reasoning:
                        on_reasoning(reasoning_piece)

                content_piece = _coerce_content(getattr(delta, "content", None))
                if content_piece:
                    result.answer += content_piece
                    if on_answer:
                        on_answer(content_piece)

            return result

        response = completion
        choice = response.choices[0]
        result.finish_reason = choice.finish_reason
        result.usage = getattr(response, "usage", None)

        message = choice.message
        reasoning_attr = getattr(message, "reasoning", None)
        if reasoning_attr:
            result.reasoning = _coerce_content(reasoning_attr)

        result.answer = _coerce_content(getattr(message, "content", ""))
        if result.answer and on_answer:
            on_answer(result.answer)
        if result.reasoning and on_reasoning:
            on_reasoning(result.reasoning)

        return result
