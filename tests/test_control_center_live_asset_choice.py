"""Control Center must choose installed, family-compatible encoder assets."""
import json
from types import SimpleNamespace

import pytest
from conftest import _preload_node

cc = _preload_node("vnccs_control_center")


@pytest.mark.parametrize("family,clips,vaes,expected_clips,expected_vae", [
    (
        "QI2",
        [("QI2 Qwen3-VL 8B Text Encoder", "qwen.safetensors")],
        [("QI2 VAE", "missing-vae.safetensors"),
         ("Installed QI2 VAE", "installed-vae.safetensors")],
        ["QI2 Qwen3-VL 8B Text Encoder"],
        "Installed QI2 VAE",
    ),
    (
        "Klein9b",
        [("Flux Klein Qwen 3 8B", "qwen.safetensors"),
         ("Unrelated T5 encoder", "t5.safetensors")],
        [("Flux 2 VAE", "flux-vae.safetensors")],
        ["Flux Klein Qwen 3 8B"],
        "Flux 2 VAE",
    ),
])
def test_installed_single_encoder_and_vae_selected(
        monkeypatch, family, clips, vaes, expected_clips, expected_vae):
    model = {"name": "Test edit model", "kind": family, "type": "unet",
             "local_path": "models/diffusion_models/edit.safetensors"}
    config = {"models": [model], "clip": [
        {"name": name, "kind": family, "type": "TextEncoder",
         "local_path": f"models/text_encoders/{path}"}
        for name, path in clips
    ], "vae": [
        {"name": name, "kind": family, "type": "VAE",
         "local_path": f"models/vae/{path}"}
        for name, path in vaes
    ], "lora": []}
    monkeypatch.setattr(cc, "_get_cc_config", lambda _repo: config)
    monkeypatch.setattr(cc, "_apply_active_installed_paths", lambda data: data)
    monkeypatch.setattr(cc, "_find_model_on_disk",
                        lambda path: (path, "missing-" not in str(path)))
    monkeypatch.setattr(cc, "_ensure_required_turbo_lora_state", lambda states, *_: states)
    monkeypatch.setattr(cc, "_model_file_signature", lambda path: path)
    captured = {}

    def load(_model, _type, _settings, _config, names, vae_name, **_kwargs):
        captured.update(clips=names, vae=vae_name)
        return object(), object(), object()

    monkeypatch.setattr(cc, "_load_model_block", load)
    monkeypatch.setattr(cc, "_apply_loras",
                        lambda model, clip, *_args, **_kwargs: (model, clip))
    state = json.dumps({"active_kind": family, "selected_type": "unet",
                        "selected_model": model["name"]})
    cc._build_control_center_pipe("test/repository", state)
    assert captured == {"clips": expected_clips, "vae": expected_vae}
