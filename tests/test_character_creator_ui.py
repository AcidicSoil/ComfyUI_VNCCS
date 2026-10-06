from pathlib import Path


SOURCE = (Path(__file__).parents[1] / "web" / "vnccs_character_creator_v2.js").read_text(encoding="utf-8")


def test_anima_resolution_selector_exposes_supported_presets():
    assert 'createCompactSelectField("Resolution", "resolution_preset", state.gen_settings)' in SOURCE
    assert '["normal", "Normal · 640 × 1536"]' in SOURCE
    assert '["high", "High · 856 × 2048"]' in SOURCE
    assert '["maximum", "Maximum · 1024 × 2456"]' in SOURCE


def test_portrait_resolution_selector_is_scoped_to_anima_and_qwen_and_persisted():
    assert 'animaResolutionWrap.style.display = "none"' in SOURCE
    assert 'const hasPortraitResolution = isAnima || isQwen;' in SOURCE
    assert 'els.animaResolutionWrap.style.display = hasPortraitResolution ? "flex" : "none"' in SOURCE
    assert 'anima: ["diffusion_model_name", "clip_name", "vae_name", "resolution_preset"' in SOURCE
    assert 'qwen_image_2_1: ["generation_mode", "diffusion_model_name", "clip_name", "vae_name", "clip_type", "resolution_preset"' in SOURCE
    assert 'resolution_preset: "normal"' in SOURCE


def test_model_selection_canonicalizes_unique_nested_registry_names():
    assert 'const canonicalAssetValue = (items, requested) =>' in SOURCE
    assert 'animaProfile[key] = canonicalAssetValue(' in SOURCE
    assert 'localAssets.text_encoders' in SOURCE
    assert 'localAssets.vae_models' in SOURCE


def test_character_creator_ui_exposes_qwen_image_21_as_peer_generation_mode():
    assert '["qwen_image_2_1", "Qwen Image 2.1"]' in SOURCE
    assert 'qwen_image_2_1:' in SOURCE
    assert 'QWEN_IMAGE21_DEFAULTS' in SOURCE
    assert 'modelPickerOpen.qwen_image_2_1' in SOURCE
    assert 'els.qwenModels' in SOURCE


def test_character_creator_qwen_mode_uses_qi2_catalog_model_encoder_and_vae():
    assert '["qi2", "qwenimage21"]' in SOURCE
    assert 'ensureQwenDefaultAux' in SOURCE
    assert 'selectQwenModel' in SOURCE
    assert 'downloadQwenBundle' in SOURCE
    assert 'clip_type: "qwen_image"' in SOURCE
