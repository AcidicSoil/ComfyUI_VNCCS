from pathlib import Path


ROOT = Path(__file__).parents[1]
EMOTION_SOURCE = (ROOT / "nodes" / "emotion_generator_v2.py").read_text()
GENERATOR_SOURCE = (ROOT / "nodes" / "character_generator.py").read_text()


def test_emotion_generator_advertises_qwen_image_21_qi2_mode():
    assert '"QI2"' in EMOTION_SOURCE
    assert "QI2_DEFAULTS" in EMOTION_SOURCE
    assert '"generation_mode": "qi2"' in EMOTION_SOURCE


def test_emotion_pipe_records_qi2_model_identity_for_downstream_conditioning():
    assert '"kind": "QI2"' in EMOTION_SOURCE
    assert "_is_qi2_pipe" in GENERATOR_SOURCE
    assert "_qi2_encode" in GENERATOR_SOURCE
    assert "_run_qi2_emotion_crop_generation" in GENERATOR_SOURCE
