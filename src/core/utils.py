"""
Lab 11 — Helper Utilities
"""
import asyncio

from core.config import get_llm_provider, PROVIDER_OPENROUTER  # noqa: F401
from core.openai_runtime import OpenAIRunner


def _is_transient_provider_error(exc: Exception) -> bool:
    """Return True for provider throttling/outage errors worth retrying."""
    text = f"{type(exc).__name__}: {exc}".upper()
    # A per-day quota cannot recover during this command. Retrying it only
    # creates noisy ADK traces and consumes time; keep retries for temporary
    # minute-level throttling and provider outages.
    if (
        "GENERATEREQUESTSPERDAYPERPROJECTPERMODEL" in text
        or "REQUESTS PER DAY" in text
        or "DAILY QUOTA" in text
    ):
        return False
    return any(marker in text for marker in (
        "429",
        "503",
        "UNAVAILABLE",
        "RESOURCE_EXHAUSTED",
        "HIGH DEMAND",
        "TIMEOUT",
        "TIMED OUT",
    ))


async def chat_with_agent(agent, runner, user_message: str, session_id=None):
    """Send a message to the agent and get the response.

    Works with OpenAIRunner (OpenAI Red / OpenRouter Blue) and Google ADK (Gemini Red).
    """
    provider = getattr(runner, "provider", None)
    if isinstance(runner, OpenAIRunner) or provider in ("openrouter", "openai"):
        text = await runner.chat(agent, user_message)
        return text, None

    from google.genai import types

    user_id = "student"
    app_name = runner.app_name

    session = None
    if session_id is not None:
        try:
            session = await runner.session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
        except (ValueError, KeyError):
            pass

    if session is None:
        try:
            session = await runner.session_service.create_session(
                app_name=app_name, user_id=user_id
            )
        except Exception:
            session = await runner.session_service.create_session(
                app_name=app_name, user_id=user_id
            )

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_message)],
    )

    max_attempts = 4
    for attempt in range(max_attempts):
        final_response = ""
        try:
            async for event in runner.run_async(
                user_id=user_id, session_id=session.id, new_message=content
            ):
                if hasattr(event, "content") and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            final_response += part.text
            break
        except Exception as exc:
            if attempt == max_attempts - 1 or not _is_transient_provider_error(exc):
                raise
            delay = 2 ** (attempt + 1)
            print(
                f"Gemini tạm thời bận; thử lại sau {delay}s "
                f"({attempt + 2}/{max_attempts})..."
            )
            await asyncio.sleep(delay)

    return final_response, session
