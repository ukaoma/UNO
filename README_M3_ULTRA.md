# UNO Image Generation with M3 Ultra GPU Acceleration

## Changes Made to Enable M3 Ultra GPU Acceleration

I've identified and fixed the issue that was causing the application to run on CPU despite having a powerful M3 Ultra GPU available. Here's what was fixed:

1. **MPS Device Detection**:
   - The app now properly detects Apple Silicon's GPU via Metal Performance Shaders (MPS)
   - Added fallback logic for when MPS isn't available
   - Added validation to ensure the MPS device works correctly

2. **Device Propagation**:
   - Modified `app.py` to pass the detected device to `inference.py`
   - Updated the `InferenceArgs` class in `inference.py` to accept a custom device parameter
   - Added proper device handling in the UNO pipeline initialization

3. **Compatibility Fixes**:
   - Added handling for model types that might not be compatible with MPS
   - Fixed parameter handling for the newly supported device types
   - Added proper "linear" positional encoding option

4. **Diagnostics**:
   - Added detailed logging about device selection and usage
   - Created test tensor allocation to verify device functionality
   - Added PyTorch version reporting to help with troubleshooting

## Benefits

Using your M3 Ultra's GPU acceleration should provide:

- **Dramatically Faster Inference**: GPU-accelerated generation can be 5-20x faster
- **Lower Memory Usage**: Proper GPU memory management reduces system RAM usage
- **Better Quality**: Can use higher quality settings in the same amount of time
- **Cooler Operation**: More efficient processing reduces thermal overhead

## How to Verify GPU Usage

When you run the app, you should now see output similar to:

```
PyTorch version: 2.6.0
Using Apple Silicon GPU via MPS
Test tensor created successfully on mps device

==================================================
🚀 Starting Ukaoma Image Generation v1.1.0
💻 System: Apple Silicon GPU (M-series) with 0.0GB VRAM
👉 Access the interface in your browser when it launches
==================================================
```

While generating, you should notice:
- Much faster generation times
- Higher CPU usage in Activity Monitor's "GPU" section
- Lower RAM usage in Activity Monitor

## Troubleshooting

If you still see "No GPU detected" or "Using CPU" messages:

1. Verify PyTorch is compiled with MPS support: `python -c "import torch; print(torch.backends.mps.is_available())"`
2. Ensure you're using PyTorch 2.0+ which has better MPS support
3. Check the terminal output for any specific errors with MPS initialization
4. Try with a smaller model first (`flux-schnell` mode)

## Launch the App

```bash
python app.py
```

If you see "Using Apple Silicon GPU via MPS" in the output, you're all set!
