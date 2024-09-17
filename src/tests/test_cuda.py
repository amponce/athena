import torch
import whisper

def test_cuda():
    # Log PyTorch and CUDA versions
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        print(f"CUDA device capability: {torch.cuda.get_device_capability(0)}")
        print(f"CUDA memory allocated: {torch.cuda.memory_allocated(0)} bytes")
        print(f"CUDA memory reserved: {torch.cuda.memory_reserved(0)} bytes")
        print(f"CUDA memory stats: {torch.cuda.memory_stats()}")

        # Perform a more complex tensor operation
        print("\nPerforming a tensor operation on CUDA:")
        a = torch.randn(3, 3).cuda()
        b = torch.randn(3, 3).cuda()
        print(f"Tensor a: {a}")
        print(f"Tensor b: {b}")
        c = torch.matmul(a, b)
        print(f"a @ b (matrix multiplication) = {c}")
    else:
        print("CUDA is not available, running on CPU.")

    # Test Whisper model loading
    print("\nTesting Whisper model loading:")
    try:
        model = whisper.load_model("tiny")
        print(f"Whisper model device: {model.device}")
        print(f"Model loaded successfully on device: {model.device}")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")

    # Check GPU memory after model load
    if torch.cuda.is_available():
        print(f"CUDA memory allocated after loading model: {torch.cuda.memory_allocated(0)} bytes")
        print(f"CUDA memory reserved after loading model: {torch.cuda.memory_reserved(0)} bytes")

    # Simple CUDA operation to confirm everything works post-load
    if torch.cuda.is_available():
        print("\nPerforming a simple post-model-loading CUDA operation:")
        d = torch.cuda.FloatTensor(2).zero_()
        print(f"Tensor d (initialized to zero): {d}")
        e = torch.randn(2).cuda()
        print(f"Tensor e (random): {e}")
        f = d + e
        print(f"d + e = {f}")

    # More detailed device properties (for additional logging)
    if torch.cuda.is_available():
        print("\nCUDA Device Properties:")
        device_properties = torch.cuda.get_device_properties(0)
        for key, value in device_properties.__dict__.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    test_cuda()