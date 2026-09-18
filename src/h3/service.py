import uuid
from typing import Any

import httpx

from .database import insert_error, insert_prompt_id, select_status
from .models import Text2VideoRequest, VideoStatus


def handle_t2v(
    client: httpx.Client, 
    request_id: uuid.UUID, 
    data: Text2VideoRequest
) -> None:
    
    r = client.post(
        "/prompt", 
        json={"prompt": data_to_workflow(data)}
    )
    
    if r.is_success:
        prompt_id = r.json()["prompt_id"]
        insert_prompt_id(request_id, prompt_id)    
    else:
        insert_error(request_id, r.text)


def get_status(request_id: uuid.UUID) -> VideoStatus | None:
    if status := select_status(request_id):
        return VideoStatus(request_id, status)


def data_to_workflow(data: Text2VideoRequest) -> dict[str, Any]:
    width = 960
    height = 544
    length = 243
    return singularity_workflow(
        data.prompt,
        width,
        height,
        length
    )


def singularity_workflow(
    prompt: str,
    width: int,
    height: int,
    length: int,
    seed: int = 12345,
    diffusion_model: str = "Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors",
    text_encoder: str = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
    video_vae: str = "minimax_h3_video_vae_int8_convrot.safetensors",
    audio_vae: str = "minimax_h3_audio_vae_fp32.safetensors",
    turbo_lora: str = "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"
) -> dict:
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": diffusion_model,
                "weight_dtype": "default",
            },
        },
    
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": text_encoder,
                "type": "minimax",
                "device": "default",
            },
        },
    
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": video_vae,
            },
        },

        "4": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": audio_vae,
            },
        },
            
        "5": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["1", 0],
                "lora_name": turbo_lora,
                "strength_model": 1.0,
            },
        },
    
        "6": {
            "class_type": "MiniMaxH3SigmaShift",
            "inputs": {
                "model": ["5", 0],
                "shift_video": 12.0,
                "shift_audio": 3.0,
            },
        },
    
        "7": {
            "class_type": "MiniMaxH3ReferenceToVideo",
            "inputs": {
                "clip": ["2", 0],
                "vae": ["3", 0],
                "audio_vae": ["4", 0],
                "prompt": prompt,
                "width": width,
                "height": height,
                "length": length,
                "ref_image_size": "match",
            },
        },
    
        "8": {
            "class_type": "RandomNoise",
            "inputs": {
                "noise_seed": seed,
            },
        },
    
        "9": {
            "class_type": "KSamplerSelect",
            "inputs": {
                "sampler_name": "euler",
            },
        },
    
        "10": {
            "class_type": "BasicScheduler",
            "inputs": {
                "model": ["6", 0],
                "scheduler": "simple",
                "steps": 4,
                "denoise": 1.0,
            },
        },
    
        "11": {
            "class_type": "BasicGuider",
            "inputs": {
                "model": ["6", 0],
                "conditioning": ["7", 0],
            },
        },
    
        "12": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["8", 0],
                "guider": ["11", 0],
                "sampler": ["9", 0],
                "sigmas": ["10", 0],
                "latent_image": ["7", 1],
            },
        },
    
        "13": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["12", 0],
                "vae": ["3", 0],
            },
        },
        
        "14": {
            "class_type": "VAEDecodeAudio",
            "inputs": {
                "samples": ["12", 0],
                "vae": ["4", 0],
            },
        },
    
        "15": {
            "class_type": "CreateVideo",
            "inputs": {
                "images": ["13", 0],
                 "audio": ["14", 0],
                "fps": 24.0,
            },
        },
    
        "16": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ["15", 0],
                "filename_prefix": "video/",
                "format": "mp4",
                "codec": "h264",
            },
        },
    } 