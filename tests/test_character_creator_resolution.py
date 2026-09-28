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


def test_qwen_image_21_defaults_match_native_comfy_workflow():
    settings = normalize_gen_settings({"generation_mode": "qwen_image_2_1"})

    assert settings["generation_mode"] == "qwen_image_2_1"
    assert settings["steps"] == 25
    assert settings["cfg"] == 1.0
    assert settings["sampler"] == "euler"
    assert settings["scheduler"] == "simple"
    assert settings["clip_type"] == "qwen_image"
    assert settings["turbo_enabled"] is False


def test_qwen_image_21_prompt_encoding_uses_scheduled_conditioning():
    class DummyClip:
        def __init__(self):
            self.calls = []

        def tokenize(self, text, **kwargs):
            self.calls.append(("tokenize", text, kwargs))
            return text

        def encode_from_tokens_scheduled(self, tokens):
            self.calls.append(("encode", tokens))
            return [["scheduled", {"text": tokens}]]

    clip = DummyClip()
    result = character_creator_v2.encode_generation_prompt(
        clip, "portrait prompt", {"generation_mode": "qwen_image_2_1"}
    )

    assert result == [["scheduled", {"text": "portrait prompt"}]]
    assert clip.calls[0] == (
        "tokenize", "portrait prompt",
        {"keep_vision": True, "prevent_empty_text": True},
    )


def test_qwen_image_21_asset_key_includes_all_selected_components():
    settings = {
        "generation_mode": "qwen_image_2_1",
        "diffusion_model_name": "model.gguf",
        "clip_name": "encoder.safetensors",
        "vae_name": "vae.safetensors",
    }

    assert character_creator_v2.generation_asset_key(settings) == (
        "qwen_image_2_1", "model.gguf", "encoder.safetensors", "vae.safetensors"
    )


def test_qwen_image_21_loras_do_not_inherit_illustrious_dmd_or_age_policy():
    calls = []

    def apply_lora(model, clip, name, strength, clip_strength=None):
        calls.append((name, strength, clip_strength))
        return model, clip

    character_creator_v2.apply_generation_loras(
        object(), object(),
        {
            "generation_mode": "qwen_image_2_1",
            "turbo_enabled": True,
            "dmd_lora_name": "wrong-dmd.safetensors",
            "age_lora_name": "wrong-age.safetensors",
            "lora_stack": [{"name": "qwen-style.safetensors", "strength": 0.7}],
        },
        {"age": 30},
        apply_lora,
    )

    assert calls == [("qwen-style.safetensors", 0.7, None)]


def test_unknown_anima_resolution_falls_back_to_normal():
    settings = normalize_gen_settings({
        "generation_mode": "anima",
        "resolution_preset": "unsupported",
    })

    assert settings["resolution_preset"] == "normal"
    assert get_generation_resolution(settings) == (640, 1536)


@pytest.mark.parametrize(
    ("preset", "expected"),
    [
        ("normal", (640, 1536)),
        ("high", (864, 2048)),
        ("maximum", (1024, 2464)),
    ],
)
def test_qwen_image_21_resolution_presets_are_native_multiples(preset, expected):
    settings = normalize_gen_settings({
        "generation_mode": "qwen_image_2_1",
        "resolution_preset": preset,
    })

    assert settings["resolution_preset"] == preset
    assert get_generation_resolution(settings) == expected
    assert expected[0] % 32 == 0
    assert expected[1] % 32 == 0


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


@pytest.mark.parametrize(
    ("model_name", "expected_loader"),
    [
        ("qwenImage21Nvfp4Q4Q3_q4GGUF.gguf", "UnetLoaderGGUF"),
        ("noctQUncensoredRealismBuiltOn_v30Base_fp8.safetensors", "UNETLoader"),
    ],
)
def test_load_qwen_image_21_assets_uses_loader_for_weight_format(
    model_name, expected_loader, tmp_path, monkeypatch
):
    names = {
        "diffusion_models": [model_name],
        "text_encoders": ["qwenImage21TextEncoderOriginal_v10_3241874.safetensors"],
        "vae": ["qwenImage21VAEOriginalBf16_v10.safetensors"],
    }
    monkeypatch.setattr(
        character_creator_v2.folder_paths,
        "get_filename_list",
        lambda category: names.get(category, []),
    )
    monkeypatch.setattr(
        character_creator_v2.folder_paths,
        "get_folder_paths",
        lambda category: [str(tmp_path / category)],
    )
    calls = []

    def fake_loader(class_names, _method_names, **kwargs):
        calls.append((class_names, kwargs))
        return object()

    monkeypatch.setattr(character_creator_v2, "_call_loader_node", fake_loader)

    character_creator_v2.load_qwen_image21_assets({
        "diffusion_model_name": model_name,
        "clip_name": names["text_encoders"][0],
        "vae_name": names["vae"][0],
    })

    assert expected_loader in calls[0][0]
    assert calls[0][1]["unet_name"] == model_name
    assert calls[1][1]["clip_name"] == names["text_encoders"][0]
    assert calls[1][1]["type"] == "qwen_image"
    assert calls[2][1]["vae_name"] == names["vae"][0]
