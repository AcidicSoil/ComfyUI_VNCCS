from pathlib import Path


SOURCE = (Path(__file__).parents[1] / "web" / "vnccs_emotion_v2.js").read_text()


def test_emotion_model_selection_canonicalizes_nested_registry_names():
    assert "const canonicalAssetValue = (items, requested) =>" in SOURCE
    assert "state.gen.clip_name = canonicalAssetValue(" in SOURCE
    assert "state.gen.vae_name = canonicalAssetValue(" in SOURCE
    assert "state.gen.diffusion_model_name = canonicalAssetValue(" in SOURCE


def test_emotion_ui_exposes_qwen_image_21_generation_mode():
    assert 'Qwen Image 2.1' in SOURCE
    assert 'setGenerationMode("qwen_image_2_1")' in SOURCE
    assert 'qwen_image_2_1' in SOURCE
    assert 'QI2' in SOURCE or 'qwenimage21' in SOURCE.lower()
