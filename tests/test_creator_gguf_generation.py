"""Keep Qwen GGUF generation on a GGUF-aware loader, never torch pickle."""

import pytest
from conftest import _preload_node

pytest.importorskip("torch")
creator = _preload_node("character_creator_v2")


def _settings(filename):
    return {
        "generation_mode": "qi2",
        "diffusion_model_name": filename,
        "clip_name": "qwen-clip.safetensors",
        "vae_name": "qwen-vae.safetensors",
    }


def test_qwen_gguf_uses_dedicated_loader_not_pytorch(monkeypatch):
    calls = []
    monkeypatch.setattr(creator, "resolve_installed_generation_assets", dict)
    monkeypatch.setattr(creator, "load_generation_clip", lambda _settings: "clip")

    def load_node(classes, methods, **kwargs):
        calls.append((classes, methods, kwargs))
        return "gguf-model" if classes == ["UnetLoaderGGUF"] else "vae"

    monkeypatch.setattr(creator, "_call_loader_node", load_node)
    monkeypatch.setattr(creator.comfy.sd, "load_diffusion_model",
                        lambda *_args, **_kwargs: pytest.fail("Native loader must not parse GGUF"),
                        raising=False)
    _model, _clip, _vae = creator.load_anima_assets(
        _settings("qwenImage21Nvfp4Q4Q3_q4GGUF.gguf"))
    assert (_model, _clip, _vae) == ("gguf-model", "clip", "vae")
    assert calls[0][0] == ["UnetLoaderGGUF"]
    assert calls[0][2]["unet_name"] == "qwenImage21Nvfp4Q4Q3_q4GGUF.gguf"


def test_qwen_gguf_missing_loader_is_explicit(monkeypatch):
    monkeypatch.setattr(creator, "resolve_installed_generation_assets", dict)
    monkeypatch.setattr(creator, "_call_loader_node", lambda *_a, **_kw: None)
    with pytest.raises(RuntimeError, match="GGUF loader"):
        creator.load_anima_assets(_settings("qwenImage21Nvfp4Q4Q3_q4GGUF.gguf"))
