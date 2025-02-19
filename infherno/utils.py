import torch

def determine_device():
    # Determine the device to use
    if torch.cuda.is_available():
        device = "cuda"  # CUDA (NVIDIA GPU)
    elif torch.backends.mps.is_available():
        device = "mps"   # MPS (Apple GPU)
    else:
        device = "cpu"   # CPU fallback
    return device


