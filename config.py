"""Small configuration module for the terminal commute agent."""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()
REQUEST_TIMEOUT_SECONDS = 8
USER_AGENT = "ReAct-Intelligent-Commute-Agent/1.0 (college-project)"
