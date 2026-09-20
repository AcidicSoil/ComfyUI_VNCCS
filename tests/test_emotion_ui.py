from pathlib import Path


SOURCE = (Path(__file__).parents[1] / "web" / "vnccs_emotion_v2.js").read_text()


def test_emotion_model_selection_canonicalizes_nested_registry_names():
    assert "const canonicalAssetValue = (items, requested) =>" in SOURCE
    assert "state.gen.clip_name = canonicalAssetValue(" in SOURCE
    assert "state.gen.vae_name = canonicalAssetValue(" in SOURCE
    assert "state.gen.diffusion_model_name = canonicalAssetValue(" in SOURCE
