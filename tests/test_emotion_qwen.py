from pathlib import Path


ROOT = Path(__file__).parents[1]
EMOTION_SOURCE = (ROOT / "nodes" / "emotion_generator_v2.py").read_text()
GENERATOR_SOURCE = (ROOT / "nodes" / "character_generator.py").read_text()


def test_emotion_generator_advertises_qwen_image_21():
    assert '"Qwen Image 2.1"' in EMOTION_SOURCE
    assert "QWEN_IMAGE21_DEFAULTS" in EMOTION_SOURCE
    assert '"qwen_image_2_1"' in EMOTION_SOURCE


def test_emotion_pipe_records_qwen_model_identity_for_downstream_conditioning():
    assert '"kind": "QwenImage21"' in EMOTION_SOURCE or '"kind": "QI2"' in EMOTION_SOURCE
    assert "_is_qwen_image21_pipe" in GENERATOR_SOURCE
    assert "keep_vision=True" in GENERATOR_SOURCE
    assert "prevent_empty_text=True" in GENERATOR_SOURCE
