from functools import lru_cache

from langchain_openai import ChatOpenAI


@lru_cache
def get_llm(model: str | None = None):
    """One client per model name. Swap in any LangChain chat model here."""
    return ChatOpenAI(model=model or "gpt-4o-mini", temperature=0)
