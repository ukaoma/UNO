import os
import gradio as gr
import torch
import json
import random
import sys
import time
import numpy as np
from PIL import Image
from pathlib import Path
from datetime import datetime
from inference import main as run_inference
from argparse import Namespace

# Create output directory if it doesn't exist
os.makedirs("output/gradio", exist_ok=True)

# Version information
VERSION = "1.1.0"
APP_TITLE = "Ukaoma Image Generation"

# Check PyTorch version
print(f"PyTorch version: {torch.__version__}")

# Check available devices (CUDA for NVIDIA GPUs, MPS for Apple Silicon)
CUDA_AVAILABLE = torch.cuda.is_available()
MPS_AVAILABLE = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()

# Set device based on availability
if CUDA_AVAILABLE:
    GPU_NAME = torch.cuda.get_device_name(0)
    VRAM = torch.cuda.get_device_properties(0).total_memory / 1024**3  # Convert to GB
    DEVICE = "cuda"
    print(f"Using NVIDIA GPU: {GPU_NAME} with {VRAM:.2f} GB VRAM")
elif MPS_AVAILABLE:
    GPU_NAME = "Apple Silicon GPU (M-series)"
    VRAM = 0  # Unfortunately, PyTorch doesn't provide a way to query Apple Silicon VRAM
    DEVICE = "mps"
    print(f"Using Apple Silicon GPU via MPS")
else:
    GPU_NAME = "No GPU detected"
    VRAM = 0
    DEVICE = "cpu"
    print("WARNING: No GPU detected, falling back to CPU. Processing will be slow.")

# Create a simple test tensor to verify device works
try:
    test_tensor = torch.zeros(1, device=DEVICE)
    print(f"Test tensor created successfully on {DEVICE} device")
except Exception as e:
    print(f"Error creating tensor on {DEVICE}: {e}")
    print("Falling back to CPU")
    DEVICE = "cpu"
    GPU_NAME = "GPU detection failed - using CPU"
    VRAM = 0

def generate_image(
    prompt,
    model_type,
    ref_images,
    width,
    height,
    steps,
    guidance,
    seed,
    only_lora,
    pe_type
):
    """Generate an image with UNO model based on the given parameters and reference images."""
    # Generate a unique ID for this run
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"output/gradio/{run_id}/refs"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Process reference images - fix for the multi-image upload issue
    # Copy uploaded files to a temp directory with proper permissions
    image_paths = []
    
    if ref_images is not None and len(ref_images) > 0:
        for i, img_file in enumerate(ref_images):
            if img_file is not None:
                # Check if it's a file path (string) or a file object
                if isinstance(img_file, str):
                    # It's already a path
                    image_paths.append(img_file)
                elif hasattr(img_file, 'name'):
                    # It's a file object with a name attribute
                    image_paths.append(img_file.name)
                else:
                    # It might be a numpy array or other object, save it as an image
                    try:
                        from PIL import Image
                        import numpy as np
                        if isinstance(img_file, np.ndarray):
                            img_path = os.path.join(temp_dir, f"ref_{i}.png")
                            Image.fromarray(img_file).save(img_path)
                            image_paths.append(img_path)
                    except Exception as e:
                        print(f"Error processing image file: {e}")
    
    if not image_paths:
        return None, "Error: No valid reference images provided. Please upload at least one image."
    
    # Create args Namespace with the values from the UI
    args = Namespace(
        prompt=prompt,
        model_type=model_type,
        image_paths=image_paths,
        width=width,
        height=height,
        ref_size=512,  # Default
        num_steps=steps,
        guidance=guidance,
        seed=seed if seed > 0 else random.randint(1, 1000000),
        offload=False,
        only_lora=only_lora,
        pe=pe_type,
        save_path=f"output/gradio/{run_id}",
        concat_refs=False,
        lora_rank=512,  # Default
        data_resolution=512,  # Default
        num_images_per_prompt=1,
        eval_json_path=None,
        device=DEVICE,  # Pass the detected device to inference.py
    )
    
    # Save args to json for reference
    os.makedirs(args.save_path, exist_ok=True)
    with open(f"{args.save_path}/args.json", "w") as f:
        # Convert Namespace to dict for JSON serialization
        args_dict = vars(args)
        # Convert paths to strings for JSON serialization
        args_dict["image_paths"] = [str(p) for p in args_dict["image_paths"]]
        json.dump(args_dict, f, indent=2)
    
    # Run the inference
    try:
        # Start the inference process
        run_inference(args)
        
        output_img = f"{args.save_path}/0_0.png"
        
        if os.path.exists(output_img):
            return output_img, f"Generation successful! Seed: {args.seed}"
        else:
            return None, "Generation failed: Output image not found"
    except Exception as e:
        error_msg = str(e)
        print(f"Error during generation: {error_msg}")
        return None, f"Generation failed: {error_msg}"

# Create UI with Custom Theme
custom_theme = gr.themes.Soft().set(
    body_background_fill="#0f172a",
    background_fill_primary="#121212",
    background_fill_secondary="#1e1e1e",
    border_color_accent="#4f46e5",
    border_color_primary="#2d2d2d", 
    color_accent="#4f46e5",
    button_primary_background_fill="#4f46e5",
    button_primary_background_fill_hover="#4338ca",
    button_primary_text_color="white",
    button_secondary_background_fill="#1e293b",
    button_secondary_background_fill_hover="#334155",
    button_secondary_text_color="white"
)

with gr.Blocks(
    title=APP_TITLE, 
    theme=custom_theme,
    css="assets/custom.css"
) as demo:
    # Header section
    gr.HTML("""<div class="header-container">""")
    gr.Markdown(
        f"""
        # {APP_TITLE}
        
        ### Create amazing images with a touch of magic - Simple & powerful image generation
        """
    )
    
    with gr.Accordion("System Info", open=False):
        gr.Markdown(f"""
        - GPU: {GPU_NAME}
        - VRAM: {VRAM:.2f} GB
        - Python: {sys.version.split()[0]}
        - PyTorch: {torch.__version__}
        """)
    gr.HTML("""</div>""")
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                prompt = gr.Textbox(label="Prompt", placeholder="Describe what you want to generate...", lines=3)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        model_type = gr.Dropdown(
                            label="Model Type", 
                            choices=["flux-schnell", "flux-base"], 
                            value="flux-schnell"
                        )
                        gr.Markdown("*Schnell is faster, while Base may generate higher quality at the cost of speed*", elem_classes="helper-text")
                    
                    with gr.Column(scale=1):
                        seed_container = gr.Group()
                        with seed_container:
                            seed = gr.Number(
                                label="Generation Seed", 
                                value=0, 
                                precision=0
                            )
                            gr.Markdown("*Controls randomness. Use 0 for unique results each time, or use the same number to recreate similar images*", elem_classes="helper-text")
                            random_seed_btn = gr.Button("🎲 Random Seed", size="sm")
                            
                            def randomize_seed():
                                return random.randint(1, 1000000)
                            
                            random_seed_btn.click(fn=randomize_seed, inputs=[], outputs=[seed])
                
                with gr.Accordion("Reference Images", open=True):
                    gr.Markdown("""
                    Upload 1-4 images that you want to include in your generation. These will guide what appears in the final image.
                    """)
                    
                    ref_images = gr.File(
                        label="Drop or upload your images here", 
                        file_count="multiple",
                        file_types=["image"],
                        elem_id="ref-images",
                        elem_classes="file-upload-box"
                    )
                    
                    # No default examples to keep branding consistent
                
                with gr.Accordion("Quality Settings", open=False, elem_classes="advanced-settings"):
                    gr.Markdown("Adjust these settings to control quality and style")
                    with gr.Row():
                        with gr.Column(scale=1):
                            width = gr.Slider(
                                label="Image Width", 
                                minimum=256, 
                                maximum=1024, 
                                step=64, 
                                value=512
                            )
                            gr.Markdown("*Larger sizes may require more memory*", elem_classes="helper-text")
                        
                        with gr.Column(scale=1):
                            height = gr.Slider(
                                label="Image Height", 
                                minimum=256, 
                                maximum=1024, 
                                step=64, 
                                value=512
                            )
                            gr.Markdown("*Larger sizes may require more memory*", elem_classes="helper-text")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            steps = gr.Slider(
                                label="Generation Steps", 
                                minimum=1, 
                                maximum=50, 
                                step=1, 
                                value=25
                            )
                            gr.Markdown("*More steps = higher quality but slower generation*", elem_classes="helper-text")
                        
                        with gr.Column(scale=1):
                            guidance = gr.Slider(
                                label="Prompt Strength", 
                                minimum=1.0, 
                                maximum=10.0, 
                                step=0.1, 
                                value=4.0
                            )
                            gr.Markdown("*How closely the image follows your prompt text*", elem_classes="helper-text")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            only_lora = gr.Checkbox(
                                label="Optimize for Speed", 
                                value=True
                            )
                            gr.Markdown("*Trade some quality for faster generation*", elem_classes="helper-text")
                        
                        with gr.Column(scale=1):
                            pe_type = gr.Dropdown(
                                label="Advanced Encoding", 
                                choices=["d", "linear"], 
                                value="d"
                            )
                            gr.Markdown("*Technical setting that affects how images are processed*", elem_classes="helper-text")
                
                with gr.Row():
                    example_prompts = [
                        "A clock on the beach under a red umbrella",
                        "A crystal ball showing a futuristic cityscape",
                        "A cat sitting in a cafe window at sunset",
                    ]
                    
                    gr.Examples(
                        examples=example_prompts,
                        inputs=prompt,
                    )
                
                generate_btn = gr.Button("✨ Create Your Image", variant="primary", elem_classes="generate-btn")
        
        with gr.Column(scale=1):
            with gr.Group():
                output_image = gr.Image(
                    label="Your Created Image", 
                    elem_id="output-image",
                    height=512
                )
                output_message = gr.Textbox(
                    label="Status", 
                    interactive=False,
                    elem_classes="status-message",
                    placeholder="Status will appear here when you generate an image"
                )
                
                with gr.Row():
                    clear_btn = gr.Button("🔄 Start Over", variant="secondary")
                    download_btn = gr.Button("💾 Save Image", variant="secondary")
                
                with gr.Accordion("Your Creation History", open=False):
                    history = gr.Gallery(label="Recent Creations", show_label=False, columns=2, height=200)
                    
                    def update_history(img):
                        # Update the history gallery with the new image
                        if img is None:
                            return []
                        return [img]
                    
                    # Update history when new image is generated
                    output_image.change(fn=update_history, inputs=[output_image], outputs=[history])
    
    # Define interactions
    generate_btn.click(
        fn=generate_image,
        inputs=[
            prompt, model_type, ref_images, 
            width, height, steps, guidance, 
            seed, only_lora, pe_type
        ],
        outputs=[output_image, output_message]
    )
    
    clear_btn.click(
        fn=lambda: (None, ""),
        inputs=[],
        outputs=[output_image, output_message]
    )
    
    # Helper function for downloads
    def download_image(img):
        if img is None:
            return None
        
        # For gradio 3.x compatibility, we need to save the image to a file first
        if isinstance(img, np.ndarray):
            # Create a temporary directory if it doesn't exist
            temp_dir = os.path.join("output", "downloads")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate a unique filename
            filename = f"ukaoma_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(temp_dir, filename)
            
            # Save the image using PIL
            Image.fromarray(img).save(filepath)
            return filepath
        elif isinstance(img, str):
            # If it's already a filepath, return it
            return img
        else:
            # Handle other types
            return None

    download_btn.click(
        fn=download_image,
        inputs=[output_image],
        outputs=[gr.File(label="Download")]
    )

    # Add footer with version info
    footer = gr.Markdown(
        f"""
        <div style="text-align: center; margin-top: 20px; opacity: 0.7; font-size: 0.8rem;">
        Ukaoma Image Generator | Powered by UNO | v{VERSION}
        </div>
        """)

# Launch the app
if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"🚀 Starting {APP_TITLE} v{VERSION}")
    print(f"💻 System: {GPU_NAME} with {VRAM:.1f}GB VRAM")
    print(f"👉 Access the interface in your browser when it launches")
    print(f"{'='*50}\n")
    
    demo.launch(
        share=False, 
        inbrowser=True,
        server_name="0.0.0.0",  # Allow access from other devices on network
        show_error=True
    )
