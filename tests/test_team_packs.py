import json
import sys
import os
import subprocess
import tempfile
import pytest
from argparse import Namespace
from pathlib import Path

import scripts.team_packs as tp


def test_build_mapping_prefers_model_and_preferred_list():
    agents_cfg = {
        "agent1": {"model": "explicit-model", "preferred_model_ids": ["first", "second"]},
        "agent2": {"preferred_model_ids": ["only-choice", "other"]},
    }
    mapping = tp._build_mapping(agents_cfg)
    assert mapping["agent1"]["model"] == "explicit-model"
    assert mapping["agent2"]["model"] == "only-choice"

def test_build_mapping_errors_on_missing_entries():
    with pytest.raises(ValueError):
        tp._build_mapping({"agent": {}})

def test_cmd_list_outputs_example_pack_names(capsys):
    # Should discover the example packs under packs/ and include their names
    tp.cmd_list(None)
    out = capsys.readouterr().out
    assert "cost-optimised-dev" in out
    assert "high-quality-prod" in out

def test_cmd_apply_invokes_subprocess_and_passes_correct_flags(monkeypatch, tmp_path):
    # Prevent removal of temp mapping file
    monkeypatch.setattr(tp.os, "remove", lambda path: None)
    calls = []
    monkeypatch.setattr(tp.subprocess, "run", lambda cmd, check: calls.append(cmd))

    # Prepare args to apply the cost-optimised-dev pack
    args = Namespace(pack_name="cost-optimised-dev", version=None)
    # Run apply command
    tp.cmd_apply(args)

    assert len(calls) == 1
    cmd = calls[0]
    # sys.executable and select-models.py path are first elements
    assert sys.executable in cmd[0]
    assert str(tp.SELECT_MODELS_SCRIPT) in cmd[1]
    # should include apply subcommand and mapping file flag
    assert "apply" in cmd
    assert "--mapping" in cmd
    # verify jurisdiction and allow-local flags correspond to manifest
    manifest = tp._select_pack(tp._load_all_manifests(), "cost-optimised-dev", None)
    idx = cmd.index("--jurisdiction") + 1
    assert cmd[idx] == manifest.jurisdiction_policy
    idx2 = cmd.index("--allow-local") + 1
    assert cmd[idx2] == manifest.allow_local
