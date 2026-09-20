import pytest

from conftest import _preload_node


pytest.importorskip("torch")

character_creator_v2 = _preload_node("character_creator_v2")
get_generation_resolution = character_creator_v2.get_generation_resolution
normalize_gen_settings = character_creator_v2.normalize_gen_settings


@pytest.mark.parametrize(
    ("preset", "expected"),
    [
        ("normal", (640, 1536)),
        ("high", (856, 2048)),
        ("maximum", (1024, 2456)),
    ],
)
def test_anima_resolution_presets(preset, expected):
    settings = normalize_gen_settings({
        "generation_mode": "anima",
        "resolution_preset": preset,
    })

    assert settings["resolution_preset"] == preset
    assert get_generation_resolution(settings) == expected


def test_unknown_anima_resolution_falls_back_to_normal():
    settings = normalize_gen_settings({
        "generation_mode": "anima",
        "resolution_preset": "unsupported",
    })

    assert settings["resolution_preset"] == "normal"
    assert get_generation_resolution(settings) == (640, 1536)


def test_illustrious_ignores_anima_resolution_preset():
    settings = normalize_gen_settings({
        "generation_mode": "illustrious",
        "resolution_preset": "maximum",
    })

    assert get_generation_resolution(settings) == (640, 1536)


def test_load_anima_assets_passes_canonical_nested_names_to_comfy_loaders(tmp_path, monkeypatch):
    import folder_paths as fp

    extra_diffusion = tmp_path / "diffusion_models"
    extra_text = tmp_path / "text_encoders"
    extra_vae = tmp_path / "vae"
    targets = {
        ("diffusion_models", r"anima\anima-base-v1.0.safetensors"): extra_diffusion / "anima" / "anima-base-v1.0.safetensors",
        ("text_encoders", r"anima\qwen_3_06b_base.safetensors"): extra_text / "anima" / "qwen_3_06b_base.safetensors",
        ("vae", r"anima\qwen_image_vae.safetensors"): extra_vae / "anima" / "qwen_image_vae.safetensors",
    }
    for target in targets.values():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x")

    names = {
        "diffusion_models": [r"anima\anima-base-v1.0.safetensors"],
        "text_encoders": [r"anima\qwen_3_06b_base.safetensors"],
        "vae": [r"anima\qwen_image_vae.safetensors"],
    }
    roots = {
        "diffusion_models": [str(extra_diffusion)],
        "text_encoders": [str(extra_text)],
        "vae": [str(extra_vae)],
    }

    monkeypatch.setattr(fp, "get_filename_list", lambda category: names.get(category, []))
    monkeypatch.setattr(fp, "get_folder_paths", lambda category: roots.get(category, []))
    monkeypatch.setattr(
        fp,
        "get_full_path",
        lambda category, name: str(targets[(category, name)])
        if (category, name) in targets else None,
    )

    calls = []

    def fake_loader(_class_names, _method_names, **kwargs):
        calls.append(kwargs)
        if "unet_name" in kwargs:
            return object()
        if "clip_name" in kwargs:
            return object()
        if "vae_name" in kwargs:
            return object()
        return None

    monkeypatch.setattr(character_creator_v2, "_call_loader_node", fake_loader)

    character_creator_v2.load_anima_assets({
        "diffusion_model_name": "anima-base-v1.0.safetensors",
        "clip_name": "qwen_3_06b_base.safetensors",
        "vae_name": "qwen_image_vae.safetensors",
        "clip_type": "stable_diffusion",
    })

    assert calls[0]["unet_name"] == r"anima\anima-base-v1.0.safetensors"
    assert calls[1]["clip_name"] == r"anima\qwen_3_06b_base.safetensors"
    assert calls[2]["vae_name"] == r"anima\qwen_image_vae.safetensors"
