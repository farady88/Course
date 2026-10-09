import os
import sys
from pathlib import Path

os.environ["ANTHROPIC_API_KEY"] = "test-key"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import anthropic
from fastapi.testclient import TestClient
import llm
from main import app

client = TestClient(app)