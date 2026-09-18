import uuid, secrets
from typing import Any
from pathlib import Path

import httpx

from src.config.constants import EXTERNAL_URL, VIDEO_DIR
from .models import Text2VideoRequest, VideoStatus
from .database import (
    insert_error, 
    update_error,
    update_success,
    insert_prompt_id, 
    select_request,
    select_filename
)

def load_mp4_bytes(url_name: str) -> bytes | None:
    if not url_name.endswith('.mp4'):
        return None     
    url_name = url_name.split('.')[0]
    if not (filename := select_filename(url_name)):
        return None

    filepath = Path(f"{VIDEO_DIR}/{filename}")
    if not filepath.exists():
        return b''

    with open(filepath, 'rb') as f:
        return f.read()


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


def get_status(
    client: httpx.Client,
    request_id: uuid.UUID
) -> VideoStatus | None:
    
    if not (row := select_request(request_id)):
        return None
    
    status = row['status']    
    if status == 'error':
        return VideoStatus(
            request_id,
            status,
            error_msg=row['error_msg']
        )
    elif status == 'success':
        return VideoStatus(
            request_id,
            status,
            video_url=f"{EXTERNAL_URL}/result/{row['url_name']}.mp4"
        )
    elif status == 'processing':
        prompt_id = row['prompt_id']
        r = client.get(f"/history/{prompt_id}")
        r.raise_for_status()
        
        # comfy queue
        if not (record := r.json().get(prompt_id, None)):
            return VideoStatus(request_id, status)

        status = record['status']
        status_str = status['status_str']
        
        # comfy processing
        if not status['completed']:
            return VideoStatus(request_id, status)
        
        # error during generation
        if status_str != 'success':
            error_msg = "Error during generation"
            update_error(request_id, error_msg)
            return VideoStatus(
                request_id,
                status="error",
                error_msg=error_msg
            )

        # successful generation
        filename = next(iter(record['outputs'].values()))['images'][0]['filename']
        url_name = secrets.token_urlsafe(12)
        update_success(request_id, filename, url_name)
        return VideoStatus(
            request_id,
            "success",
            video_url=f"{EXTERNAL_URL}/result/{url_name}.mp4"
        )       


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
                "filename_prefix": "video/_",
                "format": "mp4",
                "codec": "h264",
            },
        },
    } 