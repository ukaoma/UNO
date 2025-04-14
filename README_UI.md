# Ukaoma Image Generation

A polished, user-friendly interface for ByteDance's UNO image generation model. This GUI makes it easy to create stunning images using your local setup without introducing any breaking changes to the original model.

![UNO GUI](assets/teaser.jpg)

## Features

- **User-Friendly Interface** - Beautiful, dark-themed UI designed for ease of use
- **Multi-Image Support** - Upload up to 4 reference images to guide the generation
- **Simple Controls** - User-friendly terminology for complex AI concepts
- **Progress Indicators** - See generation progress in real-time
- **Example Images** - Quick access to sample reference images
- **Example Prompts** - Inspiration to get you started
- **Image History** - Keep track of your previous generations
- **Status Updates** - Clear feedback during the generation process
- **Optimized for M3 Ultra** - Makes full use of your 80-core GPU and 96GB unified memory

## System Requirements

- **Hardware**: Compatible with M3 Ultra with 80-core GPU and 96GB unified memory
- **Software**: Python 3.9+ with PyTorch
- **Models**: Existing UNO model weights

## Installation

This GUI integrates with your existing UNO setup. To install it:

1. Make sure you've already set up the UNO model as per the original repository instructions
2. Install the additional UI dependencies:

```bash
# Install using the provided script
./install_ui.sh

# OR install manually
pip install -r requirements_ui.txt
```

## Usage

1. Start the interface:

```bash
python app.py
```

2. The interface will open automatically in your default web browser
3. Enter a prompt describing what you want to generate
4. Upload 1-4 reference images to guide the generation
5. Adjust quality settings as needed
6. Click "Create Your Image"
7. View, save, or download your generated image

## Interface Guide

### Main Controls

- **Prompt**: Describe what you want to generate
- **Model Type**: Choose between speed (flux-schnell) and quality (flux-base)
- **Generation Seed**: Controls randomness (0 for unique images each time)
- **Reference Images**: Upload 1-4 images to guide the generation

### Quality Settings

- **Image Width/Height**: Adjust the output resolution
- **Generation Steps**: Higher values give better quality but take longer
- **Prompt Strength**: How closely to follow the prompt text
- **Optimize for Speed**: Trade some quality for faster generation
- **Advanced Encoding**: Technical setting for image processing experts

## Troubleshooting

- **No valid reference images error**: Make sure you've uploaded at least one image
- **Generation failed errors**: Check the error message in the status box for details
- **Slow generation**: Try reducing image resolution or number of steps
- **Out of memory errors**: Reduce resolution or use flux-schnell model

## Extending

The GUI is built on Gradio, making it easy to extend:

- Add new models by updating the model_type dropdown choices
- Customize the theme by modifying assets/custom.css
- Add new parameters by extending the UI elements and generate_image function

## License

This UI is released under the same license as the original UNO model.

## Acknowledgments

- Based on [ByteDance UNO](https://github.com/bytedance/UNO)
- Built with [Gradio](https://www.gradio.app/)
