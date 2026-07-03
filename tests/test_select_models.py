"""Tests for scripts/select-models.py pure functions. No network calls."""
import pytest

from .conftest import load_script

sm = load_script("select-models.py")


# --------------------------------------------------------------------------- #
# Jurisdiction classification
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    ("model_id", "expected"),
    [
        ("opencode/claude-haiku-4-5", "US"),
        ("opencode/gpt-5.1-codex", "US"),
        ("opencode/gemini-3-flash", "US"),
        ("opencode/grok-code", "US"),
        ("opencode/mistral-large", "EU"),
        ("opencode/codestral-2", "EU"),
        ("opencode/devstral-small", "EU"),
        ("opencode/cohere-command", "Sovereign"),
        ("opencode/qwen3-coder", "Global"),
        ("opencode/deepseek-v3", "Global"),
        ("opencode/kimi-k2", "Global"),
        ("opencode/some-unknown-model", "Global"),  # unknown → most restricted
    ],
)
def test_classify_jurisdiction(model_id, expected):
    assert sm.classify_jurisdiction(model_id) == expected


@pytest.mark.parametrize(
    ("policy", "allow_local", "expected"),
    [
        ("eu", "no", {"EU", "Sovereign"}),
        ("eu", "yes", {"EU", "Sovereign", "Local"}),
        ("eu+us", "no", {"EU", "Sovereign", "US"}),
        ("global", "yes", {"EU", "Sovereign", "US", "Global", "Local"}),
    ],
)
def test_allowed_jurisdictions(policy, allow_local, expected):
    assert sm.allowed_jurisdictions(policy, allow_local) == expected


# --------------------------------------------------------------------------- #
# Ollama parameter-size parsing
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    ("raw", "expected"),
    [("7.6B", 7.6), ("30B", 30.0), (" 8b ", 8.0), ("", None), (None, None), ("weird", None)],
)
def test_parse_param_billions(raw, expected):
    assert sm._parse_param_billions(raw) == expected


# --------------------------------------------------------------------------- #
# Pricing-table HTML scrape
# --------------------------------------------------------------------------- #

DOCS_HTML = """
<html><body>
<table>
  <tr><th>Model</th><th>Model ID</th></tr>
  <tr><td>GPT 5.1</td><td>gpt-5.1</td></tr>
  <tr><td>Claude Haiku 4.5</td><td>claude-haiku-4-5</td></tr>
</table>
<table>
  <tr><th>Model</th><th>Input</th><th>Output</th></tr>
  <tr><td>GPT 5.1</td><td>$1.00</td><td>$8.00</td></tr>
  <tr><td>GPT 5.1 (&gt; 272K tokens)</td><td>$2.00</td><td>$16.00</td></tr>
  <tr><td>Claude Haiku 4.5</td><td>$0.80</td><td>$4.00</td></tr>
</table>
</body></html>
"""


def test_scrape_zen_prices_joins_tables_and_collapses_tiers():
    prices = sm._scrape_zen_prices(DOCS_HTML)
    assert prices["opencode/gpt-5.1"] == {"input": "$1.00", "output": "$8.00"}
    assert prices["opencode/claude-haiku-4-5"] == {"input": "$0.80", "output": "$4.00"}


def test_scrape_zen_prices_empty_doc():
    assert sm._scrape_zen_prices("<html><body>no tables</body></html>") == {}


# --------------------------------------------------------------------------- #
# Mapping validation
# --------------------------------------------------------------------------- #

ZEN_IDS = {"opencode/gpt-5.1", "opencode/mistral-large"}
OLLAMA_IDS = {"ollama/qwen3:8b"}


def test_validate_mapping_happy_path():
    mapping = {"orchestrator": {"model": "opencode/gpt-5.1"}}
    enriched = sm.validate_mapping(mapping, "eu+us", "no", ZEN_IDS, OLLAMA_IDS)
    assert enriched["orchestrator"] == {"model": "opencode/gpt-5.1", "jurisdiction": "US"}


def test_validate_mapping_rejects_unavailable_model():
    mapping = {"orchestrator": {"model": "opencode/nonexistent-model"}}
    with pytest.raises(ValueError, match="not\\s+available"):
        sm.validate_mapping(mapping, "global", "no", ZEN_IDS, OLLAMA_IDS)


def test_validate_mapping_rejects_policy_violation():
    mapping = {"orchestrator": {"model": "opencode/gpt-5.1"}}
    with pytest.raises(ValueError, match="jurisdiction"):
        sm.validate_mapping(mapping, "eu", "no", ZEN_IDS, OLLAMA_IDS)


def test_validate_mapping_rejects_uninstalled_local_model():
    mapping = {"verifier": {"model": "ollama/notinstalled:7b"}}
    with pytest.raises(ValueError, match="not\\s+installed"):
        sm.validate_mapping(mapping, "eu", "yes", ZEN_IDS, OLLAMA_IDS)


def test_validate_mapping_rejects_unknown_namespace():
    mapping = {"verifier": {"model": "azure/gpt-4"}}
    with pytest.raises(ValueError, match="namespace"):
        sm.validate_mapping(mapping, "global", "no", ZEN_IDS, OLLAMA_IDS)
