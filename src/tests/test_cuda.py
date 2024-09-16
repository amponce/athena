import torch
import whisper 

def test_cuda():
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
    
    # Test with Whisper
    print("\nTesting Whisper model loading:")
    model = whisper.load_model("tiny")
    print(f"Whisper model device: {model.device}")

    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    # Simple CUDA operation
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        print("\nPerforming a simple CUDA operation:")
        a = torch.cuda.FloatTensor(2).zero_()
        print(f"Tensor a: {a}")
        b = torch.randn(2).cuda()
        print(f"Tensor b: {b}")
        c = a + b
        print(f"a + b = {c}")

if __name__ == "__main__":
    test_cuda()