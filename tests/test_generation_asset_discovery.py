from pathlib import Path


ROOT = Path(__file__).parents[1]
RUNTIME_FILES = [
    ROOT / "nodes" / "character_creator_v2.py",
    ROOT / "nodes" / "emotion_generator_v2.py",
    ROOT / "nodes" / "service_nodes.py",
    ROOT / "web" / "vnccs_character_creator_v2.js",
    ROOT / "web" / "vnccs_emotion_v2.js",
]
FORBIDDEN_DEFAULT_FILENAMES = [
    "qwen_image_2.1_int8_convrot.safetensors",
    "qwen3vl_8b_int8_convrot.safetensors",
    "qwen_image_2.1_vae_bf16.safetensors",
    "qwen_3_06b_base.safetensors",
    "anima-base-v1.0.safetensors",
    "anima-turbo-lora-v0.1.safetensors",
    "Qwen-Image-2.1-viggle-turbo-v0.2.1-6step-lora-r128.safetensors",
    "VNCCS_QI2_AnimeOverhaulV1.safetensors",
]


def test_runtime_generation_surfaces_do_not_require_exact_asset_filenames():
    source = "\n".join(path.read_text(encoding="utf-8") for path in RUNTIME_FILES)
    for filename in FORBIDDEN_DEFAULT_FILENAMES:
        assert filename not in source, filename


def test_current_packaged_workflows_do_not_pin_generation_assets_or_named_default_model():
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "workflows").glob("*.json"))
    for value in [*FORBIDDEN_DEFAULT_FILENAMES, "Qwen Image 2.1 INT8 ConvRot"]:
        assert value not in source, value
