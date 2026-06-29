import json
import sys
import subprocess
import tempfile
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import scripts.team_packs as tp


def _extract_list_rows(output: str):
    rows = []
    data_section = False
    for line in output.splitlines():
        if not data_section:
            if line.startswith("-"):
                data_section = True
            continue
        if not line.strip():
            continue
        rows.append(line)
    return rows


def test_build_mapping_prefers_model_and_preferred_list():
    agents_cfg = {
        "builder-pipelines": {
            "model": "explicit-model",
            "preferred_model_ids": ["first", "second"],
        },
        "verifier": {"preferred_model_ids": ["only-choice", "other"]},
    }
    mapping = tp._build_mapping(agents_cfg)
    assert mapping["builder-pipelines"]["model"] == "explicit-model"
    assert mapping["verifier"]["model"] == "only-choice"

def test_build_mapping_errors_on_missing_entries():
    with pytest.raises(ValueError):
        tp._build_mapping({"agent": {}})


def test_build_mapping_errors_on_unknown_agent(monkeypatch):
    monkeypatch.setattr(tp, "_load_valid_agent_ids", lambda: {"known"})
    with pytest.raises(ValueError, match="unknown agent 'bad'"):
        tp._build_mapping({"bad": {"model": "x"}})


def test_build_mapping_requires_model_or_preferred(monkeypatch):
    monkeypatch.setattr(tp, "_load_valid_agent_ids", lambda: {"agent-one"})
    with pytest.raises(ValueError, match="must define either 'model' or a non-empty 'preferred_model_ids'"):
        tp._build_mapping({"agent-one": {}})


def test_build_mapping_errors_on_empty_preferred_list(monkeypatch):
    monkeypatch.setattr(tp, "_load_valid_agent_ids", lambda: {"agent-two"})
    agents_cfg = {"agent-two": {"preferred_model_ids": []}}
    with pytest.raises(ValueError, match="must define either 'model' or a non-empty 'preferred_model_ids'"):
        tp._build_mapping(agents_cfg)

def test_cmd_list_outputs_example_pack_names(capsys):
    # Should discover the example packs under packs/ and include their names
    tp.cmd_list(None)
    out = capsys.readouterr().out
    assert "cost-optimised-dev" in out
    assert "high-quality-prod" in out

def test_cmd_list_deduplicates_duplicate_packs(monkeypatch, capsys):
    manifest_base = tp.PackManifest(
        name="demo-pack",
        version="1.0.0",
        dir_label="v1",
        description="demo",
        jurisdiction_policy="eu+us",
        allow_local="no",
        optimisation_focus="cost",
        agents={"agent": {"model": "foo"}},
        path=tp.REPO_ROOT / "packs" / "demo-pack" / "v1" / "pack.yaml",
    )
    manifest_template = tp.PackManifest(
        name="demo-pack",
        version="1.0.0",
        dir_label="v1",
        description="demo",
        jurisdiction_policy="eu+us",
        allow_local="no",
        optimisation_focus="cost",
        agents={"agent": {"model": "foo"}},
        path=tp.REPO_ROOT
        / "templates"
        / "opencode-config"
        / "packs"
        / "demo-pack"
        / "v1"
        / "pack.yaml",
    )

    monkeypatch.setattr(
        tp, "_load_all_manifests", lambda: [manifest_base, manifest_template]
    )
    tp.cmd_list(None)
    out = capsys.readouterr().out
    rows = _extract_list_rows(out)
    assert len(rows) == 1
    assert "demo-pack" in rows[0]


def test_normalize_allow_local_accepts_numeric_input():
    assert tp._normalize_allow_local(1) == "yes"
    assert tp._normalize_allow_local(0) == "no"
    assert tp._normalize_allow_local("Y") == "yes"


def test_normalize_jurisdiction_rejects_invalid_value():
    with pytest.raises(ValueError, match="Unsupported jurisdiction_policy"):
        tp._normalize_jurisdiction("apac")


def test_load_manifest_requires_all_fields(tmp_path):
    pack_path = tmp_path / "packs" / "demo" / "v1" / "pack.yaml"
    pack_path.parent.mkdir(parents=True)
    pack_path.write_text(
        """
name: demo
version: 1.0.0
description: demo pack
jurisdiction_policy: eu
agents:
  agent: {model: x}
        """,
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required fields"):
        tp._load_manifest(pack_path)


def test_load_all_manifests_warns_on_invalid_yaml(monkeypatch, tmp_path, capsys):
    bad_pack = tmp_path / "packs" / "demo" / "v1" / "pack.yaml"
    bad_pack.parent.mkdir(parents=True)
    bad_pack.write_text("name: [unbalanced", encoding="utf-8")

    monkeypatch.setattr(tp, "_discover_pack_files", lambda: [bad_pack])
    manifests = tp._load_all_manifests()
    assert manifests == []
    err = capsys.readouterr().err
    assert "invalid YAML" in err


def test_select_pack_errors_when_pack_missing():
    with pytest.raises(ValueError, match="No pack named"):
        tp._select_pack([], "missing", None)


def test_select_pack_errors_when_version_missing():
    manifest = tp.PackManifest(
        name="demo",
        version="1.0.0",
        dir_label="v1",
        description="desc",
        jurisdiction_policy="eu",
        allow_local="no",
        optimisation_focus="cost",
        agents={"agent": {"model": "foo"}},
        path=tp.REPO_ROOT / "packs" / "demo" / "v1" / "pack.yaml",
    )
    with pytest.raises(ValueError, match="does not have version 'v2'"):
        tp._select_pack([manifest], "demo", "v2")


def test_load_valid_agent_ids_requires_agents_block(tmp_path, monkeypatch):
    config_path = tmp_path / "opencode.json"
    config_path.write_text(json.dumps({"agent": {}}), encoding="utf-8")
    monkeypatch.setattr(tp, "OPENCODE_CONFIG_PATH", config_path)
    with pytest.raises(ValueError, match="does not define any agents"):
        tp._load_valid_agent_ids()


def test_cmd_apply_invokes_subprocess_and_passes_correct_flags(monkeypatch, tmp_path):
    # Prevent removal of temp mapping file
    monkeypatch.setattr(tp.os, "remove", lambda path: None)
    calls = []

    class DummyCompleted:
        def __init__(self, stdout="", stderr=""):
            self.stdout = stdout
            self.stderr = stderr

    monkeypatch.setattr(
        tp.subprocess,
        "run",
        lambda *args, **kwargs: (calls.append(args[0]) or DummyCompleted("ok", "")),
    )

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


def test_cmd_apply_surfaces_subprocess_failure(monkeypatch, capsys):
    removed_paths = []
    real_remove = tp.os.remove

    def tracking_remove(path):
        removed_paths.append(path)
        return real_remove(path)

    monkeypatch.setattr(tp.os, "remove", tracking_remove)

    orig_ntf = tempfile.NamedTemporaryFile
    created = []

    def tracking_ntf(*args, **kwargs):
        tmp = orig_ntf(*args, **kwargs)
        created.append(tmp.name)
        return tmp

    monkeypatch.setattr(tp.tempfile, "NamedTemporaryFile", tracking_ntf)

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=99,
            cmd=args[0],
            stderr="model apply failed\n",
        )

    monkeypatch.setattr(tp.subprocess, "run", fake_run)

    args = Namespace(pack_name="cost-optimised-dev", version=None)

    with pytest.raises(subprocess.CalledProcessError):
        tp.cmd_apply(args)

    err = capsys.readouterr().err
    assert "Pack apply failed: model apply failed" in err
    assert created, "temp file should have been created"
    assert removed_paths == created
    for path in created:
        assert not Path(path).exists()


def test_parser_help_mentions_validate_and_create():
    parser = tp._build_parser()
    help_text = parser.format_help()
    assert "validate" in help_text
    assert "create-from-current" in help_text


def test_parser_supports_validate_command():
    parser = tp._build_parser()
    args = parser.parse_args(["validate", "demo-pack"])
    assert args.command == "validate"
    assert args.pack_name == "demo-pack"
    assert callable(args.func)


def test_parser_supports_create_from_current_command():
    parser = tp._build_parser()
    args = parser.parse_args([
        "create-from-current",
        "--name",
        "demo",
        "--major",
        "1",
        "--description",
        "Demo pack",
        "--optimisation-focus",
        "cost",
    ])
    assert args.command == "create-from-current"
    assert callable(args.func)


def _build_demo_manifest(path: Path, allow_local="no"):
    return tp.PackManifest(
        name="demo",
        version="1.0.0",
        dir_label="v1",
        description="demo pack",
        jurisdiction_policy="eu+us",
        allow_local=allow_local,
        optimisation_focus="cost",
        agents={"builder-pipelines": {"model": "opencode/good"}},
        path=path,
    )


def test_cmd_validate_passes_when_models_available(monkeypatch, capsys, tmp_path):
    manifest = _build_demo_manifest(tmp_path / "packs" / "demo" / "v1" / "pack.yaml")
    monkeypatch.setattr(tp, "_load_all_manifests", lambda: [manifest])
    monkeypatch.setattr(tp, "_ensure_select_models_script", lambda: None)

    def fake_run(*args, **kwargs):
        payload = {"zen": [{"id": "opencode/good"}], "ollama": []}
        return SimpleNamespace(stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(tp.subprocess, "run", fake_run)

    args = Namespace(pack_name="demo", version=None, all=False)
    tp.cmd_validate(args)
    out = capsys.readouterr().out
    assert "[OK]" in out
    assert "Pack 'demo' VALID" in out


def test_cmd_validate_fails_when_model_missing(monkeypatch, capsys, tmp_path):
    manifest = _build_demo_manifest(tmp_path / "packs" / "demo" / "v1" / "pack.yaml")
    monkeypatch.setattr(tp, "_load_all_manifests", lambda: [manifest])
    monkeypatch.setattr(tp, "_ensure_select_models_script", lambda: None)

    def fake_run(*args, **kwargs):
        payload = {"zen": [], "ollama": []}
        return SimpleNamespace(stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(tp.subprocess, "run", fake_run)

    args = Namespace(pack_name="demo", version=None, all=False)
    with pytest.raises(SystemExit):
        tp.cmd_validate(args)
    out = capsys.readouterr().out
    assert "MISSING" in out
    assert "Pack 'demo' INVALID" in out


def test_cmd_validate_flags_disallowed_local(monkeypatch, capsys, tmp_path):
    manifest = _build_demo_manifest(
        tmp_path / "packs" / "demo" / "v1" / "pack.yaml",
        allow_local="no",
    )
    manifest.agents["builder-pipelines"] = {"model": "ollama/custom"}
    monkeypatch.setattr(tp, "_load_all_manifests", lambda: [manifest])
    monkeypatch.setattr(tp, "_ensure_select_models_script", lambda: None)

    def fake_run(*args, **kwargs):
        payload = {"zen": [], "ollama": [{"id": "ollama/custom"}]}
        return SimpleNamespace(stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(tp.subprocess, "run", fake_run)

    args = Namespace(pack_name="demo", version=None, all=False)
    with pytest.raises(SystemExit):
        tp.cmd_validate(args)
    out = capsys.readouterr().out
    assert "DISALLOWED" in out
    assert "Pack 'demo' INVALID" in out


def test_cmd_create_from_current_generates_pack(monkeypatch, tmp_path):
    repo_root = tmp_path
    templates_root = repo_root / "templates" / "opencode-config"
    templates_root.mkdir(parents=True)

    manifest_path = repo_root / "manifest.yaml"
    manifest_data = {
        "jurisdiction_policy": "EU+US-Sovereign",
        "agents": {
            "builder-pipelines": {
                "role": "Code-Generation",
                "model": "fallback",
            }
        },
    }
    manifest_path.write_text(yaml.safe_dump(manifest_data), encoding="utf-8")

    opencode_path = repo_root / "opencode.json"
    opencode_path.write_text(
        json.dumps({"agent": {"builder-pipelines": {"model": "opencode/primary"}}}),
        encoding="utf-8",
    )

    agent_config_path = repo_root / "agent_config.py"
    agent_config_path.write_text(
        "SECURITY_POLICY = {\n    'allowed_jurisdictions': ['EU', 'Local']\n}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(tp, "REPO_ROOT", repo_root)
    monkeypatch.setattr(tp, "PACKS_ROOT", repo_root / "packs")
    monkeypatch.setattr(tp, "TEMPLATE_PACKS_ROOT", repo_root / "templates" / "opencode-config" / "packs")
    monkeypatch.setattr(tp, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(tp, "OPENCODE_CONFIG_PATH", opencode_path)
    monkeypatch.setattr(tp, "AGENT_CONFIG_PATH", agent_config_path)
    monkeypatch.setattr(tp, "PACK_SEARCH_PATHS", [tp.PACKS_ROOT, tp.TEMPLATE_PACKS_ROOT])

    args = Namespace(
        name="demo-pack",
        major="1",
        description="Demo export",
        optimisation_focus="cost",
    )
    tp.cmd_create_from_current(args)

    pack_file = repo_root / "packs" / "demo-pack" / "v1" / "pack.yaml"
    template_file = repo_root / "templates" / "opencode-config" / "packs" / "demo-pack" / "v1" / "pack.yaml"
    assert pack_file.exists()
    assert template_file.exists()

    data = yaml.safe_load(pack_file.read_text(encoding="utf-8"))
    assert data["jurisdiction_policy"] == "eu+us"
    assert data["allow_local"] == "yes"
    assert data["agents"]["builder-pipelines"]["model"] == "opencode/primary"
    assert data["agents"]["builder-pipelines"]["role"] == "Code-Generation"


def test_cmd_validate_requires_pack_when_not_all(monkeypatch, tmp_path):
    manifest = _build_demo_manifest(tmp_path / "packs" / "demo" / "v1" / "pack.yaml")
    monkeypatch.setattr(tp, "_load_all_manifests", lambda: [manifest])
    monkeypatch.setattr(tp, "_ensure_select_models_script", lambda: None)

    with pytest.raises(SystemExit, match="Pack name is required"):
        tp.cmd_validate(Namespace(pack_name=None, version=None, all=False))


def test_cmd_validate_all_iterates_over_every_manifest(monkeypatch, tmp_path):
    manifest_ok = tp.PackManifest(
        name="good-pack",
        version="1.0.0",
        dir_label="v1",
        description="desc",
        jurisdiction_policy="eu+us",
        allow_local="no",
        optimisation_focus="cost",
        agents={"builder-pipelines": {"model": "opencode/good"}},
        path=tmp_path / "packs" / "good" / "v1" / "pack.yaml",
    )
    manifest_bad = tp.PackManifest(
        name="bad-pack",
        version="1.0.0",
        dir_label="v1",
        description="desc",
        jurisdiction_policy="eu+us",
        allow_local="no",
        optimisation_focus="cost",
        agents={"builder-pipelines": {"model": "opencode/bad"}},
        path=tmp_path / "packs" / "bad" / "v1" / "pack.yaml",
    )

    monkeypatch.setattr(tp, "_load_all_manifests", lambda: [manifest_ok, manifest_bad])
    monkeypatch.setattr(tp, "_ensure_select_models_script", lambda: None)

    validated = []

    def fake_validate(manifest):
        validated.append(manifest.name)
        return manifest.name != "bad-pack"

    monkeypatch.setattr(tp, "_validate_pack_against_catalog", fake_validate)

    with pytest.raises(SystemExit):
        tp.cmd_validate(Namespace(pack_name=None, version=None, all=True))

    assert validated == ["good-pack", "bad-pack"]
