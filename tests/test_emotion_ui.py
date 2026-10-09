from pathlib import Path


SOURCE = (Path(__file__).parents[1] / "web" / "vnccs_emotion_v2.js").read_text()


def test_emotion_ui_exposes_qwen_image_21_generation_mode():
    assert 'Qwen Image 2.1' in SOURCE
    assert 'setGenerationMode("qi2")' in SOURCE
    assert '"qi2"' in SOURCE
    assert 'QI2' in SOURCE or 'qwenimage21' in SOURCE.lower()
