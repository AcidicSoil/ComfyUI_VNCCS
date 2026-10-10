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


def test_flux1_checkpoint_in_klein_folder_is_not_classified_as_klein(tmp_path):
    import json
    import struct
    path = tmp_path / "fluxedUpFluxNSFW_111.safetensors"
    header = json.dumps({
        "model.diffusion_model.img_in.weight": {
            "dtype": "F16", "shape": [3072, 64], "data_offsets": [0, 393216]
        }
    }).encode()
    path.write_bytes(struct.pack("<Q", len(header)) + header)
    assert center._local_model_family(
        "klein/fluxedUpFluxNSFW_111.safetensors", "unet", full_path=str(path)
    ) is None


def test_klein9b_checkpoint_header_still_supported(tmp_path):
    import json
    import struct
    path = tmp_path / "working-9b.safetensors"
    header = json.dumps({
        "img_in.weight": {
            "dtype": "F16", "shape": [4096, 128], "data_offsets": [0, 1048576]
        }
    }).encode()
    path.write_bytes(struct.pack("<Q", len(header)) + header)
    assert center._local_model_family(
        "klein-2-9b/working-9b.safetensors", "unet", full_path=str(path)
    ) == ("Klein9b", "unet")


def test_recognizes_prefixed_ray_qwen21_convrot_unet(tmp_path):
    import json
    import struct

    path = tmp_path / "rayQwen21_v1Int8Convrot.safetensors"
    keys = [
        "txt_in.text_norm.weight",
        "modulation.1.weight",
        "transformer_blocks.0.attn.norm_q.weight",
        "img_in.weight",
        "proj_out.weight",
        "transformer_blocks.0.img_mlp.out.weight",
    ]
    header = json.dumps({"model.diffusion_model." + key: {} for key in keys}).encode()
    path.write_bytes(struct.pack("<Q", len(header)) + header)

    assert center._local_model_family(
        path.name, "unet", full_path=str(path)
    ) == ("QI2", "unet")


def test_ray_name_does_not_make_flux_or_klein_checkpoint_qi2(tmp_path):
    import json
    import struct

    path = tmp_path / "rayQwen21_v1Int8Convrot.safetensors"
    for input_shape in ([3072, 64], [4096, 128]):
        header = json.dumps({
            "model.diffusion_model.img_in.weight": {
                "dtype": "F16", "shape": input_shape, "data_offsets": [0, 1]
            }
        }).encode()
        path.write_bytes(struct.pack("<Q", len(header)) + header)
        assert center._local_model_family(
            path.name, "unet", full_path=str(path)
        ) is None
