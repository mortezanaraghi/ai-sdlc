from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    mock_llm: bool
    hitl_mode: str
    default_model: str
    fallback_model: str


def settings() -> Settings:
    return Settings(
        data_dir=Path(os.environ.get("AI_SDLC_DATA_DIR", ".aisdlc-data")),
        mock_llm=os.environ.get("AI_SDLC_MOCK_LLM", "1") == "1",
        hitl_mode=os.environ.get("AI_SDLC_HITL_MODE", "auto"),
        default_model=os.environ.get("AI_SDLC_MODEL", "claude-opus-4-7"),
        fallback_model=os.environ.get("AI_SDLC_FALLBACK_MODEL", "claude-sonnet-4-6"),
    )
