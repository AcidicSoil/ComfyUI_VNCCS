"""Casting previews must be executable native ComfyUI prompt nodes."""
from __future__ import annotations

import base64
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from conftest import _preload_node

creator = _preload_node("character_creator_v2")


def test_casting_node_registers_as_output_node_with_prompt_inputs():
    key = "VNCCSStudioCastingPreview"
    node = creator.NODE_CLASS_MAPPINGS[key]
    assert node.OUTPUT_NODE is True
    assert node.RETURN_TYPES == ()
    assert set(node.INPUT_TYPES()["required"]) == {"request_json", "nonce"}


def test_casting_node_preserves_png_for_standard_comfy_history(monkeypatch, tmp_path):
    png = b"\x89PNG\r\n\x1a\n" + b"representative"
    calls = []
    def generated(payload):
        calls.append(payload)
        return SimpleNamespace(status=200, text=json.dumps({
            "image": base64.b64encode(png).decode()
        }))
    monkeypatch.setattr(creator, "_generate_preview_response", generated)
    monkeypatch.setattr(creator.folder_paths, "get_temp_directory", lambda: str(tmp_path), raising=False)
    request = {"character":"studio-test", "gen_settings":{"seed":123}}
    node = creator.VNCCSStudioCastingPreview()
    output = node.generate(json.dumps(request), nonce="first")
    image = output["ui"]["images"][0]
    assert image["type"] == "temp"
    assert image["subfolder"] == "VNCCSStudioCasting"
    assert (tmp_path / image["subfolder"] / image["filename"]).read_bytes() == png
    assert calls == [request]
    second = node.generate(json.dumps(request), nonce="second")
    assert second["ui"]["images"][0]["filename"] != image["filename"]


def test_casting_node_reports_generation_errors_as_failed_prompt(monkeypatch):
    monkeypatch.setattr(creator, "_generate_preview_response",
                        lambda data: SimpleNamespace(status=500, text="Qwen loader failed"))
    with pytest.raises(RuntimeError, match="Qwen loader failed"):
        creator.VNCCSStudioCastingPreview().generate(json.dumps({
            "character":"test", "gen_settings":{"seed":1}}), nonce="test")


def test_casting_node_rejects_bad_request_before_inference(monkeypatch):
    monkeypatch.setattr(creator, "_generate_preview_response",
                        lambda data: pytest.fail("must not infer"))
    with pytest.raises(ValueError, match="generation settings"):
        creator.VNCCSStudioCastingPreview().generate('{"character":"test"}')
