"""Local model classification must not confuse Wan Animate with Anima."""
from conftest import _preload_node

center = _preload_node("vnccs_control_center")


def test_wan_animate_is_not_anima():
    assert center._local_model_family(
        "wan2.2/wan22Animate14bFp16_v20.safetensors", "unet"
    ) is None


def test_real_anima_models_remain_discoverable():
    assert center._local_model_family(
        "anima/animaOverdrive_animaOverdriveV1.safetensors", "unet"
    ) == ("Anima", "unet")
